# 第一部分、实现爬取豆瓣电影《热辣滚烫》影评数据和Excel存储
#定义代码运行所需要的所有库
import requests
from lxml import etree
from openpyxl import Workbook
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# 设置请求头，模拟浏览器行为
def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
# 获取豆瓣新片榜网页内容
def get_douban_chart(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        print("网络请求出错:", e)
        return None
# 解析电影信息
def extract_movie_info(context):
    try:
        name =context.xpath('.//*[@class="avatar"]//@title')[0]
        # 定义一个列表，包含所有可能的评分等级class
        rating_classes = ['allstar10 rating', 'allstar20 rating', 'allstar30 rating', 'allstar40 rating', 'allstar50 rating']
        for rating_class in rating_classes:
            grade_element = context.xpath(f'.//*[@class="{rating_class}"]')
            if grade_element:
                grade = grade_element[0].get('title')
                break  # 如果找到，就跳出循环
        else:
            grade = "无"  # 如果循环正常结束，说明没有找到任何评分等级
        time = context.xpath('.//*[@class="comment-time "]/@title')[0]
        ip_address = context.xpath('.//*[@class="comment-location"]/text()')[0]
        content = context.xpath('.//*[@class="short"]/text()')[0]
        support_num = context.xpath('.//*[@class="votes vote-count"]/text()')[0]
        movie_info = {
            "name": name,
            "grade": grade,
            "ip_address":ip_address,
            "time": time,
            "content": content,
            "support_num": support_num,
        }
        return movie_info
    except IndexError as e:
     return None
# 提取并保存电影信息到 Excel 文件
def save_to_excel(movie_list):
    try:
        wb = Workbook()
        ws = wb.active
        ws.append(["用户名", "评价", "ip属地", "发表时间", "评价内容", "支持人数"])
        for movie in movie_list:
            ws.append([movie['name'], movie['grade'], movie['ip_address'], movie['time'], movie['content'], movie['support_num']])
        wb.save("豆瓣电影《热辣滚烫》详细信息.xlsx")
        print("数据已成功保存到Excel文件中")
    except Exception as e:
        print("保存到Excel文件时出错:", e)
# 爬取影评的主函数
def main(url):
    try:
        headers = get_headers()
        movie_list = []
        data = get_douban_chart(url, headers)
        if data:
            html_response = etree.HTML(data)
            # 使用XPath定位电影信息的元素
            contexts = html_response.xpath('//*[@class="comment-item "]')
            for context in contexts:
                # 提取电影信息并添加到电影列表中
                movie_info = extract_movie_info(context)
                if movie_info:
                    movie_list.append(movie_info)
            # 保存电影信息到Excel文件
            save_to_excel(movie_list)
    except Exception as e:
        print("出错:", e)
# 调用主函数
if __name__ == "__main__":
    url = 'https://movie.douban.com/subject/36081094/comments?start=0&limit=100&status=P&sort=new_score'
main(url)
# 第二部分、实现豆瓣电影《热辣滚烫》好评和差评词云图绘制（代码接上）
# 读取Excel文件
df = pd.read_excel("豆瓣电影《热辣滚烫》详细信息.xlsx")
# 读取停用词文件并创建停用词集合
def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set([line.strip() for line in file.readlines()])
    return stopwords
# 定义清洗和分词函数，同时去除停用词
def clean_and_segment(text, stopwords):
    words = jieba.cut(text, cut_all=False)
    return " ".join([word for word in words if word not in stopwords])
# 生成词云图的函数
def generate_wordcloud(text, title, font_path, stopwords):
    # 对文本进行清洗和分词
    processed_text = clean_and_segment(text, stopwords)
    # 创建词云对象并指定字体路径
    wordcloud = WordCloud(font_path=font_path, width=800, height=400).generate(processed_text)
    # 显示词云图
    plt.figure(figsize=(8, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # 不显示坐标轴
    plt.show()
    wordcloud.to_file(f'{title}_wordcloud.png')# 保存词云图
# 指定停用词文件路径，注意这里我从网上查找的停用词列表
stopwords_file_path = 'D:\我的学习资料\专业劳动\停用词列表.txt'
# 加载停用词
stopwords = load_stopwords(stopwords_file_path)
# 指定字体路径
font_path = 'C:/Windows/Fonts/SimHei.ttf'
# 分类评价并生成词云图
def classify_reviews_and_generate_wordclouds(df, stopwords, font_path):
    # 分类评价
    good_reviews = df[df['评价'].isin(['推荐', '力荐', '还行'])]
    bad_reviews = df[df['评价'].isin(['很差', '较差'])]
    # 合并好评的评价内容
    good_reviews_text = " ".join(good_reviews['评价内容'].astype(str).values)
    # 生成好评的词云图
    generate_wordcloud(good_reviews_text, '好评', font_path, stopwords)
    # 合并差评的评价内容
    bad_reviews_text = " ".join(bad_reviews['评价内容'].astype(str).values)
    # 生成差评的词云图
    generate_wordcloud(bad_reviews_text, '差评', font_path, stopwords)
# 执行函数
classify_reviews_and_generate_wordclouds(df, stopwords, font_path)
# 第三部分、实现豆瓣电影《热辣滚烫》评价分布饼状图的绘制（代码接上）
# 读取Excel文件
df = pd.read_excel("豆瓣电影《热辣滚烫》详细信息.xlsx")
# 过滤出特定的评分类别，并去除空值
valid_ratings = ['推荐', '力荐', '还行', '较差', '很差']
ratings = df['评价'].dropna()
filtered_ratings = ratings[ratings.isin(valid_ratings)]
# 将过滤后的评分数据转换为一个列表，用于饼状图的数值部分
ratings_list = filtered_ratings.tolist()
# 创建一个空的列表用于存放每个评分的计数
ratings_count = []
# 对每个评分进行计数
for rating in valid_ratings:
    ratings_count.append(ratings_list.count(rating))
# 饼状图的标签设置为评分值
labels = valid_ratings
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
# 使用Matplotlib绘制饼状图
plt.figure(figsize=(10, 8))  # 设置图形的大小
plt.pie(ratings_count, labels=labels, autopct='%1.1f%%', startangle=140)  # 绘制饼状图
plt.title('《热辣滚烫》评论的评分分布图')  # 添加标题
plt.axis('equal')  # 设置图形的纵横比
plt.show()# 显示图形
# 第四部分、实现豆瓣电影《热辣滚烫》IP属地分布条形图的绘制（代码接上）
# 读取Excel文件
df = pd.read_excel("豆瓣电影《热辣滚烫》详细信息.xlsx")
# 提取IP属地数据
ip_locations = df['ip属地'].dropna()  # 去除空值
# 统计不同属地的出现次数
location_counts = ip_locations.value_counts()  # value_counts() 函数会返回每个值的出现次数
# 绘制柱状图
plt.figure(figsize=(10, 8))  # 设置图形的大小
location_counts.plot(kind='bar')  # 绘制柱状图
plt.title('《热辣滚烫》评论的IP属地分布图')  # 添加标题
plt.xlabel('IP属地')  # X轴标签
plt.ylabel('数量')  # Y轴标签
# 设置Y轴刻度为整数
plt.yticks(range(0, max(location_counts)+1, 1))
plt.show()  # 显示图形
# 第五部分、实现豆瓣电影《热辣滚烫》发表时间分布折线图的绘制（代码接上）
# 读取Excel文件
df = pd.read_excel("豆瓣电影《热辣滚烫》详细信息.xlsx")
# 提取发表时间数据
times = df['发表时间'].dropna()  # 去除空值
# 将时间字符串转换为datetime对象，并设置为索引
times = pd.to_datetime(times)
df['发表时间'] = times
df.set_index('发表时间', inplace=True)  # 将发表时间设置为索引
# 按天对数据进行重采样并计数
daily_comments = df.resample('D').count()
# 绘制折线图
plt.figure(figsize=(10, ))  # 设置图形的大小
plt.plot(daily_comments.index, daily_comments, marker='o')  # 绘制折线图
plt.title('《热辣滚烫》评论的发表时间分布图')  # 添加标题
plt.xlabel('日期')  # X轴标签
plt.ylabel('评论数量')  # Y轴标签
plt.grid(True)  # 显示网格
date_format = mdates.DateFormatter('%Y-%m-%d')  # 设置日期格式
plt.gca().xaxis.set_major_formatter(date_format)  # 应用日期格式
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))  # 设置刻度间隔为5天
plt.xticks(rotation=45)  # 旋转X轴的日期标签，便于阅读
plt.tight_layout()  # 自动调整子图参数, 使之填充整个图像区域
plt.show()  # 显示图形