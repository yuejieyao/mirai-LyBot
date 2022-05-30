import time
import uuid
from io import BytesIO

import requests
from PIL import Image, ImageFont, ImageDraw


def create_sign_pic(award_info, content):
    info_font = ImageFont.truetype('modules/resource/font/sarasa-mono-sc-bold.ttf', 26)
    info_color = "#474747"
    bg_color = "#F5F5F7"
    w_icon, h_icon = 50, 50
    icon_url, name, cnt = award_info['icon'], award_info['name'], award_info['cnt']
    icon = Image.open(fp=BytesIO(requests.get(url=icon_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/78.0.3904.70 Safari/537.36 '
    }).content))
    icon = icon.convert('RGBA')
    icon = icon.resize(size=(w_icon, h_icon))

    w_content, h_content = info_font.getsize_multiline(content)
    w, h = max([w_content, w_icon]), h_icon + h_content
    img = Image.new('RGBA', (w + 20, h + 10), bg_color)
    draw = ImageDraw.Draw(img)
    draw.text((10 + w_icon, h_icon / 2 - 10), f"{name} X {cnt}", info_color, info_font)
    draw.text((5, h_icon + 10), content, info_color, info_font)
    img.paste(icon, (5, 5), icon)

    img = img.convert('RGB')
    path = f'modules/resource/temp/{uuid.uuid1()}.png'
    img.save(path)
    return path


def create_abyss_pic(role, abyss):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/78.0.3904.70 Safari/537.36'}
    info_font = ImageFont.truetype('modules/resource/font/sarasa-mono-sc-bold.ttf', 20)
    cnt_font = ImageFont.truetype('modules/resource/font/sarasa-mono-sc-bold.ttf', 16)
    info_color = "#474747"
    bg_color = "#F5F5F7"
    bg_5star = "#8e5c22"
    bg_4str = "#604879"
    w_icon_side, h_icon_side = 35, 35
    w_icon_reveal, h_icon_reveal = 120, 120

    # 基础信息
    content1 = f"UID: {role['game_uid']}  昵称: {role['nickname']}  等级: {role['level']}\n"
    content1 += f"本期深渊您已到达: {abyss['max_floor']}"
    _, h_content1 = info_font.getsize_multiline(content1)

    # 出战次数rank,有4名
    content2 = "您出战次数最多的角色:\n"
    _, h_content2 = info_font.getsize_multiline(content2)
    img_rank_reveal = Image.new('RGBA', (25 + w_icon_reveal * 4, h_icon_reveal + h_content2 + 10), bg_color)
    rank_reveal = abyss['reveal_rank']
    for i in range(len(rank_reveal)):
        reveal = rank_reveal[i]
        # avatar_id = reveal['avatar_id']
        rarity = int(reveal['rarity'])
        icon_url = reveal['avatar_icon']
        cnt = reveal['value']
        icon = Image.new('RGBA', (w_icon_reveal, h_icon_reveal + 20), bg_color)
        content = requests.get(url=icon_url, headers=headers).content
        icon_bg = Image.new('RGBA', (w_icon_reveal, h_icon_reveal), bg_5star if rarity == 5 else bg_4str)
        icon_fg = Image.open(BytesIO(content))
        icon_fg = icon_fg.convert('RGBA')
        icon_fg = icon_fg.resize(size=(w_icon_reveal, h_icon_reveal))
        icon_bg.paste(icon_fg, (0, 0), icon_fg)
        icon.paste(icon_bg, (0, 0), icon_bg)
        icon_draw = ImageDraw.Draw(icon)
        icon_draw.text((w_icon_reveal / 2 - 15, 5 + h_icon_reveal - 5), f"{cnt}次", info_color, cnt_font)
        img_rank_reveal.paste(icon, (5 + i * (w_icon_reveal + 5), 5), icon)

    time.sleep(1)
    img_info = Image.new('RGBA', (img_rank_reveal.width, h_icon_side * 3 + 10), bg_color)
    # 击破数rank
    rank_defeat = abyss['defeat_rank'][0]
    img_rank_defeat = Image.new('RGBA', (int(img_info.width / 2), h_icon_side), bg_color)
    img_rank_defeat_draw = ImageDraw.Draw(img_rank_defeat)
    img_rank_defeat_draw.text((5, 5 + h_icon_side / 2 - 10), f"最大击破数: {rank_defeat['value']}", info_color, cnt_font)
    icon_fg_rank_defeat = Image.open(fp=BytesIO(requests.get(url=rank_defeat['avatar_icon'], headers=headers).content))
    icon_fg_rank_defeat = icon_fg_rank_defeat.convert('RGBA')
    icon_fg_rank_defeat = icon_fg_rank_defeat.resize(size=(w_icon_side, h_icon_side))
    img_rank_defeat.paste(icon_fg_rank_defeat, (img_rank_defeat.width - 5 - w_icon_side, 5), icon_fg_rank_defeat)
    # 最强一击
    rank_damage = abyss['damage_rank'][0]
    img_rank_damage = Image.new('RGBA', (int(img_info.width / 2), h_icon_side), bg_color)
    img_rank_damage_draw = ImageDraw.Draw(img_rank_damage)
    img_rank_damage_draw.text((5, 5 + h_icon_side / 2 - 10), f"最强一击: {rank_damage['value']}", info_color, cnt_font)
    icon_fg_rank_damage = Image.open(fp=BytesIO(requests.get(url=rank_damage['avatar_icon'], headers=headers).content))
    icon_fg_rank_damage = icon_fg_rank_damage.convert('RGBA')
    icon_fg_rank_damage = icon_fg_rank_damage.resize(size=(w_icon_side, h_icon_side))
    img_rank_damage.paste(icon_fg_rank_damage, (img_rank_damage.width - 5 - w_icon_side, 5), icon_fg_rank_damage)
    # 承伤Rank
    rank_take_damage = abyss['take_damage_rank'][0]
    img_rank_take_damage = Image.new('RGBA', (int(img_info.width / 2), h_icon_side), bg_color)
    img_rank_take_damage_draw = ImageDraw.Draw(img_rank_take_damage)
    img_rank_take_damage_draw.text((5, 5 + h_icon_side / 2 - 10), f"最高承伤: {rank_take_damage['value']}", info_color,
                                   cnt_font)
    icon_fg_rank_take_damage = Image.open(fp=BytesIO(requests.get(
        url=rank_take_damage['avatar_icon'], headers=headers).content))
    icon_fg_rank_take_damage = icon_fg_rank_take_damage.convert('RGBA')
    icon_fg_rank_take_damage = icon_fg_rank_take_damage.resize(size=(w_icon_side, h_icon_side))
    img_rank_take_damage.paste(icon_fg_rank_take_damage, (img_rank_take_damage.width -
                                                          5 - w_icon_side, 5), icon_fg_rank_take_damage)
    # 元素战技释放数
    rank_normal_skill = abyss['normal_skill_rank'][0]
    img_rank_normal_skill = Image.new('RGBA', (int(img_info.width / 2), h_icon_side), bg_color)
    img_rank_normal_skill_draw = ImageDraw.Draw(img_rank_normal_skill)
    img_rank_normal_skill_draw.text((5, 5 + h_icon_side / 2 - 10),
                                    f"战技释放数: {rank_normal_skill['value']}", info_color, cnt_font)
    icon_fg_rank_normal_skill = Image.open(fp=BytesIO(requests.get(
        url=rank_normal_skill['avatar_icon'], headers=headers).content))
    icon_fg_rank_normal_skill = icon_fg_rank_normal_skill.convert('RGBA')
    icon_fg_rank_normal_skill = icon_fg_rank_normal_skill.resize(size=(w_icon_side, h_icon_side))
    img_rank_normal_skill.paste(icon_fg_rank_normal_skill,
                                (img_rank_normal_skill.width - 5 - w_icon_side, 5), icon_fg_rank_normal_skill)
    # 元素爆发次数
    rank_energy_skill = abyss['energy_skill_rank'][0]
    img_rank_energy_skill = Image.new('RGBA', (int(img_info.width / 2), h_icon_side), bg_color)
    img_rank_energy_skill_draw = ImageDraw.Draw(img_rank_energy_skill)
    img_rank_energy_skill_draw.text((5, 5 + h_icon_side / 2 - 10),
                                    f"爆发释放数: {rank_energy_skill['value']}", info_color, cnt_font)
    icon_fg_rank_energy_skill = Image.open(fp=BytesIO(requests.get(
        url=rank_energy_skill['avatar_icon'], headers=headers).content))
    icon_fg_rank_energy_skill = icon_fg_rank_energy_skill.convert('RGBA')
    icon_fg_rank_energy_skill = icon_fg_rank_energy_skill.resize(size=(w_icon_side, h_icon_side))
    img_rank_energy_skill.paste(icon_fg_rank_energy_skill,
                                (img_rank_normal_skill.width - 5 - w_icon_side, 5), icon_fg_rank_energy_skill)

    # 第9-12层
    # floors = abyss['floors']
    img_info.paste(img_rank_defeat, (0, 0), img_rank_defeat)
    img_info.paste(img_rank_damage, (img_rank_defeat.width, 0), img_rank_damage)
    img_info.paste(img_rank_take_damage, (0, img_rank_defeat.height), img_rank_take_damage)
    img_info.paste(img_rank_normal_skill, (img_rank_take_damage.width, img_rank_defeat.height), img_rank_normal_skill)
    img_info.paste(img_rank_energy_skill, (0, img_rank_defeat.height +
                                           img_rank_take_damage.height), img_rank_energy_skill)

    img = Image.new('RGBA', (10 + img_rank_reveal.width, 5 + h_content1 +
                             img_info.height + 5 + h_content2 + img_rank_reveal.height), bg_color)
    draw = ImageDraw.Draw(img)
    draw.text((5, 5), content1, info_color, info_font)
    draw.text((5, 10 + h_content1 + img_info.height), content2, info_color, info_font)
    img.paste(img_info, (5, 10 + h_content1), img_info)
    img.paste(img_rank_reveal, (5, h_content1 + img_info.height + h_content2), img_rank_reveal)

    img = img.convert('RGB')
    path = f'modules/resource/temp/{uuid.uuid1()}.png'
    img.save(path)
    return path


def create_abyss_floor_pic(role, abyss, index: int):
    bnum = {9: '九', 10: '十', 11: '十一', 12: '十二'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/78.0.3904.70 Safari/537.36'}
    info_font = ImageFont.truetype('modules/resource/font/sarasa-mono-sc-bold.ttf', 20)
    cnt_font = ImageFont.truetype('modules/resource/font/sarasa-mono-sc-bold.ttf', 16)
    info_color = "#474747"
    bg_color = "#F5F5F7"
    bg_5star = "#8e5c22"
    bg_4str = "#604879"
    w_icon_floor, h_icon_floor = 120, 120
    # 0123对应9 10 11 12 4层
    floor = abyss['floors'][index - 9]

    # 基础信息
    content1 = f"UID: {role['game_uid']}  昵称: {role['nickname']}  等级: {role['level']}\n"
    content1 += f"深境螺旋第{bnum[index]}层    ★{floor['star']}/{floor['max_star']}"
    _, h_content1 = info_font.getsize_multiline(content1)

    w_img, h_img = 25 + w_icon_floor * 4, 0

    img_battles = []
    # 每层3间,每间分上半下半,一间一张图
    for level in floor['levels']:
        content2 = f"第{level['index']}间    ★{level['star']}/{level['max_star']}"
        _, h_content2 = info_font.getsize_multiline(content2)
        # 宽度为4张图宽度+间距,高度为2图高度+标题
        img_battle = Image.new('RGBA', (w_img, (h_icon_floor + 25) * 2 + h_content2), bg_color)
        content2_draw = ImageDraw.Draw(img_battle)
        content2_draw.text((5, 0), content2, info_color, info_font)
        for r in range(len(level['battles'])):
            battle = level['battles'][r]
            time.sleep(1)
            for i in range(len(battle['avatars'])):
                avatar = battle['avatars'][i]
                rarity = int(avatar['rarity'])
                icon_url = avatar['icon']
                lv = avatar['level']
                icon = Image.new('RGBA', (w_icon_floor, h_icon_floor + 25), bg_color)
                content = requests.get(url=icon_url, headers=headers).content
                icon_bg = Image.new('RGBA', (w_icon_floor, h_icon_floor), bg_5star if rarity == 5 else bg_4str)
                icon_fg = Image.open(BytesIO(content))
                icon_fg = icon_fg.convert('RGBA')
                icon_fg = icon_fg.resize(size=(w_icon_floor, h_icon_floor))
                icon_bg.paste(icon_fg, (0, 0), icon_fg)
                icon.paste(icon_bg, (0, 0), icon_bg)
                icon_draw = ImageDraw.Draw(icon)
                icon_draw.text((w_icon_floor / 2 - 15, 5 + h_icon_floor - 5), f"Lv.{lv}", info_color, cnt_font)
                img_battle.paste(icon, (5 + i * (w_icon_floor + 5), h_content2 + 5 + r * (h_icon_floor + 25)), icon)
        # 每间的图出完加入列表
        img_battles.append(img_battle)

    # 循环结束后,计算总高度
    h_img = h_content1 + 5 + sum([i.height for i in img_battles]) + 5

    # 绘制img
    img = Image.new('RGBA', (w_img, h_img), bg_color)
    draw = ImageDraw.Draw(img)
    draw.text((5, 5), content1, info_color, info_font)
    for i in range(len(img_battles)):
        img_battle = img_battles[i]
        img.paste(img_battle, (0, 10 + h_content1 + i * img_battle.height), img_battle)
    img = img.convert('RGB')
    path = f'modules/resource/temp/{uuid.uuid1()}.png'
    img.save(path)
    return path
