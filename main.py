import pandas as pd
import re
from collections import Counter
from urllib.parse import urlparse

# Function to extract URLs from a string


def extract_urls(s):
    return re.findall(r"(https?://\S+)", s)

# Function to extract the domain from a URL


def extract_domain(url):
    return urlparse(url).netloc


# Read the file
with open("_chat.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Process each line
data = []
total_line_count = len(lines)
print("Processing number of lines: ", total_line_count)
line_count = 0
for line in lines:
    line_count += 1
    parts = re.match(
        r"\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)", line)
    if parts:
        date, time, sender, message = parts.groups()
        datetime_obj = pd.to_datetime(date, dayfirst=True)
        joined_in_2023 = "joined using this group's invite link" in message and datetime_obj.year == 2023
        data.append([date, time, sender, message, joined_in_2023])
    print("Processed line: ", line_count, "out of", total_line_count)

# Create a DataFrame
df = pd.DataFrame(
    data, columns=["Date", "Time", "Sender", "Message", "Joined_in_2023"])

# Convert 'Date' to datetime
df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True)

# Filter for 2023 messages excluding 'joined_in_2023' messages
df_2023 = df[(df["DateTime"].dt.year == 2023) & (~df["Joined_in_2023"])].copy()

# Total number of messages in 2023
total_messages_2023 = len(df_2023)

# Number of messages sent per month
messages_per_month = df_2023.groupby(df_2023["DateTime"].dt.month).size()

# Number of Unique New Joiners in 2023
unique_new_joiners_count_2023 = df[df["Joined_in_2023"]]["Sender"].nunique()

# Number of Unique Message Senders (excluding new joiners messages)
unique_senders_count = df_2023["Sender"].nunique()

# Top 5 Active Members
top_5_active_members = df_2023["Sender"].value_counts().head(10)
top_5_active_members_percentage = (
    top_5_active_members / total_messages_2023) * 100

# Top 5 Most Shared Website Domains
df_2023["URLs"] = df_2023["Message"].apply(extract_urls)
all_domains = [extract_domain(url)
               for url_list in df_2023["URLs"] for url in url_list]
domain_counts = Counter(all_domains)
top_5_shared_domains = domain_counts.most_common(10)

# Most Active Day
most_active_day = df_2023["DateTime"].dt.date.value_counts().idxmax()

# Most Active Week
df_2023["Week"] = df_2023["DateTime"].dt.isocalendar().week
most_active_week = df_2023["Week"].value_counts().idxmax()

# Most Active Month
most_active_month = df_2023["DateTime"].dt.month.value_counts().idxmax()

# Top 5 Longest Message Authors
df_2023["MessageWordCount"] = df_2023["Message"].apply(
    lambda x: len(x.split()))
top_5_longest_message_authors = df_2023.groupby(
    "Sender")["MessageWordCount"].sum().nlargest(10)

# Output Results
print("\n\n ========= Results ========= \n\n")
print("Number of Unique New Joiners in 2023:", unique_new_joiners_count_2023)

print("\nNumber of Messages Sent Per Month in 2023:")
for month, count in messages_per_month.items():
    print(f"Month {month}: {count} messages")

print("Number of Unique Message Senders (excluding new joiners):",
      unique_senders_count)

print("Top 10 Active Members and their percentages of total messages:\n")
for sender, count in top_5_active_members.items():
    percentage = (count / total_messages_2023) * 100
    print(f"{sender}: {count} messages ({percentage:.2f}%)")

print("\nTop 10 Most Shared Website Domains:", top_5_shared_domains)

print("\nMost Active Day of the Year:", most_active_day)

print("\nMost Active Week of the Year:", most_active_week)

print("\nMost Active Month of the Year:", most_active_month)

print("\nTop 10 Longest Message (words) Authors:\n",
      top_5_longest_message_authors)

print("Total messages in 2023 (excluding new joiner messages):", total_messages_2023)
