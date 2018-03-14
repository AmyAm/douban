#!/usr/bin/python3
#-*- coding:UTF-8 -*-
__author__ = 'linen'

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import jieba    #分词包
import pandas as pd
import numpy    #numpy计算包
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.figsize'] = (2, 4)#视图窗口的大小
from wordcloud import WordCloud#词云包
import os
# os.chdir('F:/1network/project/py')
f = open('comments.txt','a',encoding='utf-8')

#分析网页函数
def getNowPlayingMovie_list(url): 
	position='https://movie.douban.com/cinema/nowplaying/'+url
	# html = urlopen('https://movie.douban.com/cinema/nowplaying/jiangmen/')
	html = urlopen(position)
	bsObj=BeautifulSoup(html, "html.parser")
	nowplaying_movie = bsObj.findAll('div',{'id':'nowplaying'})
	nowplaying_movie_list = nowplaying_movie[0].findAll('li',{'class':'list-item'})
	nowplaying_list=[]
	for item in nowplaying_movie_list:
		nowplaying_dict={}
		nowplaying_dict['id']=item['id']
		nowplaying_dict['name']=item['data-title']
		nowplaying_list.append(nowplaying_dict)
	return nowplaying_list

# 以电影“寻梦环游记”为例，找到其短评网址：https://movie.douban.com/subject/20495023/comments
#爬取评论函数
def getCommentsById(movieId, pageNum): 
	if pageNum>0: 
		start = (pageNum-1) * 20 
	else: 
		return False 
	requrl='https://movie.douban.com/subject/'+movieId +'/comments'+'?' +'start=' + str(start) + '&limit=20'
	print(requrl)
	reap = urlopen(requrl)
	bsreap=BeautifulSoup(reap, "html.parser")
	comment_div_list = bsreap.findAll('div',{'class':'comment'})
	eachCommentList=[]
	for item in comment_div_list:
		if item.findAll('p')[0].string is not None:
			eachCommentList.append(item.findAll('p')[0].string)
	return eachCommentList

# 数据写入文件
def writeFile(s,parameter):
	f.write(s)
	f.write('\n')
	f.write(parameter)
	f.write('\n\n\n')

def main(url):
	commentList = []
	NowPlayingMovie_list = getNowPlayingMovie_list(url)
	# 获取前五页的短评数据
	for i in range(5):    
		num = i + 1 
		commentList_temp = getCommentsById(NowPlayingMovie_list[7]['id'], num)
		commentList.append(commentList_temp)

	#将列表中的数据转换为字符串
	comments=''
	for k in range(len(commentList)):
		comments=comments+(str(commentList[k])).strip()

	writeFile('原始短评数据：',comments)

	# 数据清洗，正则匹配，只留汉字
	pattern = re.compile(r'[\u4e00-\u9af5]+')
	filterdata=re.findall(pattern,comments)
	cleaned_comments = ''.join(filterdata)

	writeFile('数据清洗后的短评数据：',cleaned_comments)

	# 进行中文分词操作
	segment = jieba.lcut(cleaned_comments)

	f.write('进行中文分词操作：\n')
	for item in segment:
		f.write(item)
		f.write('\t')
	f.write('\n\n\n')

	# 为中文分词加上序列号
	words_df=pd.DataFrame({'segment':segment})

	words_df_trans = str(words_df)
	writeFile('为中文分词加上序列号：',words_df_trans)

	# 去除停用词
	stopwords=pd.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\n",names=['stopword'], encoding='utf-8')	
	words_df=words_df[~words_df.segment.isin(stopwords.stopword)]

	words_df_trans = str(words_df)
	writeFile('去除停用词后的分词：',words_df_trans)

	# 词频统计
	words_stat=words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size})
	words_stat=words_stat.reset_index().sort_values(by=["计数"],ascending=False)

	words_stat_trans=str(words_stat)
	writeFile('词频统计：',words_stat_trans)

	# 用词云显示
	wordcloud=WordCloud(font_path="simhei.ttf",background_color="white",max_font_size=80) 
	word_frequence = {x[0]:x[1] for x in words_stat.head(1000).values} 

	word_frequence_trans=str(word_frequence)
	writeFile('词频字典：',word_frequence_trans)
	
	f.close()

	wordcloud=wordcloud.fit_words(word_frequence)
	plt.imshow(wordcloud)
	plt.show()
	# plt.imsave('F:/1network/project/py/jiangmen.jpg',wordcloud)
	plt.imsave('jiangmen.jpg',wordcloud)

# 主函数
position='jiangmen'
main(position)



