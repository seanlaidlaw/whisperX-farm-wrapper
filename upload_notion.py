#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import json
from datetime import datetime, timezone

NOTION_TOKEN = ""
DATABASE_ID = ""
creation_date = sys.argv[1]


class NotionConnection:
    def __init__(self, sec_token, database_id: str):
        self.database_id = database_id
        self.headers = {
            "Authorization": "Bearer " + sec_token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def get_page(self):
        url = f'https://api.notion.com/v1/databases/{self.database_id}/query'
        payload = {'page_size': 100}
        r = requests.post(url, json=payload, headers = self.headers)

        result_dict = r.json()

        with open('db.json', 'w', encoding='utf8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)

        results = result_dict['results']

        return results

    def create_entry(self, title):
        url = f'https://api.notion.com/v1/pages'
        parent = {'database_id': self.database_id}
        newPageData = {
                       "parent": parent,
                       "icon": {"type": "emoji", "emoji": "🗒️" },
                       "properties": {
                                      "Name": { "title": [ { "text": { "content": title } } ] },
                                      "Date": { "type": "date", "date": {"start": creation_date}}
                                      }
                       }


        r = requests.post(url, json=newPageData, headers = self.headers)

        result_dict = r.json()
        print(result_dict)
        return result_dict['id']

    def create_block_obj(self, data):
        block_data = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": data
                        }
                    }
                ]
            }
        }
        return block_data

    def add_blocks_to_page(self, page_id, block_data):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        print(url)

        block_data = {"children": block_data}

        r = requests.patch(url, headers=self.headers, json=block_data)

        if r.status_code == 200:
            print("Block added")
        else:
            print("Error:", r.status_code, r.text)



ls = os.listdir()
for file in ls:
    if file.endswith(".transcript.md"):
        print("Reading: " + file)
        title = os.path.splitext(os.path.splitext(file)[0])[0] # the first [0] removes the .md, and the second the .transcript
        with open(file, 'r') as f:
            lines = f.readlines()
            notion_blocks = []
            notion_database = NotionConnection(NOTION_TOKEN, DATABASE_ID)
            new_entry_id = notion_database.create_entry(title)
            for line in lines:
                block = notion_database.create_block_obj(line.strip())
                notion_blocks.append(block)

            for i in range(0, len(notion_blocks), 99):
                subarray = notion_blocks[i:i+99]
                notion_database.add_blocks_to_page(new_entry_id, subarray)
        os.unlink(file)
