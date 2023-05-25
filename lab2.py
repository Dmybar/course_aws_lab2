import boto3

# Let's use Amazon S3
s3 = boto3.resource('s3')

print("Print your bucker:")
bucket_name = input()

# зчитування з сайтів інформації та запис у json файли
import urllib

url1 = "https://bank.gov.ua/NBU_Exchange/exchange_site?start=20210101&end=20211231&valcode=eur&sort=exchangedate&order=desc&json"
wp = urllib.request.urlopen(url1)
text = wp.read()
   
out=open('eur.json', 'wb')
out.write(text)
out.close()

url2 = "https://bank.gov.ua/NBU_Exchange/exchange_site?start=20210101&end=20211231&valcode=usd&sort=exchangedate&order=desc&json"
wp = urllib.request.urlopen(url2)
text = wp.read()
   
out=open('usd.json', 'wb')
out.write(text)
out.close()

# перетворення json у csv файли через pandas, та завантаження її на S3
import pandas as pd
df1 = pd.read_json("eur.json")
df1.to_csv("eur.csv")
df2 = pd.read_json("usd.json")
df2.to_csv("usd.csv")


data = open('eur.csv', 'rb')
s3.Bucket(bucket_name).put_object(Key='eur.csv', Body=data)
data.close()

data = open('usd.csv', 'rb')
s3.Bucket(bucket_name).put_object(Key='usd.csv', Body=data)
data.close()

# завантаження  csv файлів з S3 назад
s3_client = boto3.client('s3')
with open('eur_down.csv', 'wb') as f:
    s3_client.download_fileobj(bucket_name, 'eur.csv', f)
with open('usd_down.csv', 'wb') as f:
    s3_client.download_fileobj(bucket_name, 'usd.csv', f)

# проста візуалізація, збереження графіку та відвантаження його на S3
import seaborn as sns
import matplotlib.pyplot as plt

df1 = pd.read_csv("eur_down.csv")
df2 = pd.read_csv("usd_down.csv")

df1['exchangedate'] = pd.to_datetime(df1['exchangedate'],dayfirst=True)
df2['exchangedate'] = pd.to_datetime(df2['exchangedate'],dayfirst=True)

df = pd.concat([df1, df2], ignore_index=True)

plt.figure(figsize=(15,10))
sns.lineplot(data = df, x = "exchangedate",y = "rate_per_unit", hue = 'txt')

plt.savefig("plot.png")

data = open('plot.png', 'rb')
s3.Bucket(bucket_name).put_object(Key='plot.png', Body=data)
data.close()