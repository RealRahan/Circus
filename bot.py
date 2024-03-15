import discord
from discord.ext import commands
import random
import sys
import json
import datetime
from keep_alive import keep_alive

prefix="."
romid=1214174154438221846
intents = discord.Intents().all()
client=commands.Bot(command_prefix=prefix, intents=intents, case_insensitive=True)
client.remove_command("help")

@client.event
async def on_ready():
 print(f"تم تشغيل بوت {client.user.name} بنجاح")
 await client.change_presence(activity=discord.Game(name=f"{prefix}help"))

@client.command()
async def help(ctx):
 e=discord.Embed(title="**المساعدة**", description=f"""**
1-{prefix}`help`
إظهار جميع الاوامر
2-{prefix}`ping`
سرعة الإستجابة
3-{prefix}`daily`
4-{prefix}`bdaily`
لأخذ المكافأة اليومية الثانيه (متاحه فقط لـ <@&1195702880716476537> ..)
أخذ المكافأة اليومية
5-{prefix}`s`
لإظهار رصيدك
6-{prefix}`give/gv`
لتحويل السيركو
7-{prefix}`top/t`
اغنى اعضاء السيرفر
{prefix}`shop`
لعرض الرتب المتوفرة
8-{prefix}`rob/ro`
سرقة سيركو من شخص معين
9-{prefix}`deposit/dep`
لإيداع السيركو وحمايتها من السارقين
10-{prefix}`pull`
سحب السيركو (لشراء الرتب، الخ)

اكتب الأوامر فقط في روم <#1214174154438221846>
**""", color=ctx.author.color)
 e.set_thumbnail(url="https://fontmeme.com/permalink/240310/7f4de2c774f4be4039a5251ab4c848b0.png")
 e.set_image(url="https://images-ext-2.discordapp.net/external/K5qbyGsaKZoFkxbujT7ysrx_Zqe16KIijDVjsDeYOzQ/https/i.imgflip.com/8j4o6c.gif")
 msg=await ctx.send(embed=e)
 await msg.add_reaction("<:Serko:1216407871680544931>")

@client.command()
@commands.guild_only()
async def ping(ctx):
 await ctx.send(f"**{round(client.latency * 1000)}ms**")

@client.command()
async def s(ctx, member: discord.Member=None):
    if ctx.channel.id == romid:
     if member == None:
      member = ctx.author
     await open_account(member)
     users = await get_bank_data()
     wallet_amt = users[str(member.id)]["wallet"]
     bank_amt = users[str(member.id)]["bank"]
     em = discord.Embed(title=f"👤 {member.name}",color = discord.Color.orange())
     em.set_thumbnail(url=member.avatar)
     em.add_field(name="💵 |", value=f"{wallet_amt}")
     em.add_field(name="🏦 |", value=f"{bank_amt}")
     msg=await ctx.send(embed= em)
     await msg.add_reaction("<:Serko:1216407871680544931>")

@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
     await open_account(ctx.author)
     user = ctx.author
     users = await get_bank_data()
     if ctx.channel.id == romid:
      earnings = random.randrange(3000)
      em=discord.Embed(description=f"**حصلت على {earnings} سيركو**", color=ctx.author.color)
      em.set_thumbnail(url="https://fontmeme.com/permalink/240310/e637c9bbce427c17ba8087f604b64553.png")
      msg=await ctx.send(embed=em)
      await msg.add_reaction("<:Serko:1216407871680544931>")
      users[str(user.id)]["wallet"] += earnings
      with open("mainbank.json",'w') as f:
          json.dump(users,f)

@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def bdaily(ctx):
     await open_account(ctx.author)
     user = ctx.author
     users = await get_bank_data()
     if ctx.channel.id == romid:
      role = discord.utils.get(ctx.guild.roles, name="Circus Booster")
      if role in ctx.author.roles:
       earnings = random.randrange(3000)
       em=discord.Embed(description=f"**حصلت على {earnings} سيركو مرة أخرى**", color=ctx.author.color)
       em.set_thumbnail(url="https://fontmeme.com/permalink/240310/e637c9bbce427c17ba8087f604b64553.png")
       msg=await ctx.send(embed=em)
       await msg.add_reaction("<:Serko:1216407871680544931>")
      else:
       msg=await ctx.reply("**يجب عليك عمل بوست للسيرفر لأخذ المكافأة الثانية**", mention_author=False)
       await msg.add_reaction("<:Serko:1216407871680544931>")
      users[str(user.id)]["wallet"] += earnings
      with open("mainbank.json",'w') as f:
          json.dump(users,f)

@daily.error
async def daily_error(ctx, error): 
    if isinstance(error, commands.CommandOnCooldown):
        time=f"{error.retry_after/3600:.2f}"
        await ctx.send(f"**خذ قسطاً من الراحة ! ، يمكنك العمل بعد {time} ساعة**")
 
@bdaily.error
async def bdaily_error(ctx, error): 
    if isinstance(error, commands.CommandOnCooldown):
       time=f"{error.retry_after/3600:.2f}"
       await ctx.send(f"**خذ قسطاً من الراحة ! ، يمكنك العمل بعد {time} ساعة**")

@client.command()
async def pull(ctx,amount=None):
    if ctx.channel.id == romid:
     await open_account(ctx.author)
     if amount == None:
         msg=await ctx.send("**يرجى كتابة العدد**")
         await msg.add_reaction("<:Serko:1216407871680544931>")
         return

     bal = await update_bank(ctx.author)
     amount = int(amount)
     if amount > bal[0]:
         await ctx.send("**لاتمتلك مال كافي**")
         return
     if amount < 0:
         msg=await ctx.send("**اكتب العدد بشكل صحيح**")
         await msg.add_reaction("<:Serko:1216407871680544931>")
         return
     await update_bank(ctx.author,amount)
     await update_bank(ctx.author,-1*amount,'bank')
     em=discord.Embed(description=f"**تم سحب {amount} سيركو**", color=ctx.author.color)
     em.set_thumbnail(url="https://fontmeme.com/permalink/240310/7f4de2c774f4be4039a5251ab4c848b0.png")
     msg=await ctx.send(embed=em)
     await msg.add_reaction("<:Serko:1216407871680544931>")


@client.command(aliases=['dep'])
async def deposit(ctx,amount:int = None):
    if ctx.channel.id == romid:
     if amount == None:
         await ctx.send("**يرجى كتابة العدد**")
         return
     users = await get_bank_data()
     bank = users[str(ctx.author.id)]["bank"]
     bal = await update_bank(ctx.author)
     amount = int(amount)
     if amount > bal[0]:
      msg=await ctx.send("**لاتمتلك مال كافي**")
      await msg.add_reaction("<:Serko:1216407871680544931>")
      return
     if amount < 0:
      msg=await ctx.send("**اكتب العدد بشكل صحيح**")
      await msg.add_reaction("<:Serko:1216407871680544931>")
      return
     await update_bank(ctx.author,-1*amount)
     await update_bank(ctx.author,amount,'bank')
     em=discord.Embed(description=f"**تم ايداع {amount} سيركو**", color=ctx.author.color)
     em.set_thumbnail(url="https://fontmeme.com/permalink/240310/7f4de2c774f4be4039a5251ab4c848b0.png")
     msg=await ctx.send(embed=em)
     await msg.add_reaction("<:Serko:1216407871680544931>")

@client.command(aliases=['gv'])
async def give(ctx,member : discord.Member,amount = None):
    if ctx.channel.id == romid:
     await open_account(ctx.author)
     await open_account(member)
     if amount == None:
         msg=await ctx.send("**يرجى كتابة العدد**")
         await msg.add_reaction("<:Serko:1216407871680544931>")
         return
     bal = await update_bank(ctx.author)
     if amount == 'all':
         amount = bal[0]
     amount = int(amount)
     if amount > bal[0]:
         msg=await ctx.send("**لاتمتلك مال كافي**")
         await msg.add_reaction("<:Serko:1216407871680544931>")
         return
     if amount < 0:
         msg=await ctx.send("**يرجى كتابة عدد**")
         return

     await update_bank(ctx.author,-1*amount,'bank')
     await update_bank(member,amount,'bank')
     em=discord.Embed(description=f"**قمت بإعطاء {member} {amount} سيركو**", color=ctx.author.color)
     em.set_thumbnail(url="https://fontmeme.com/permalink/240310/7f4de2c774f4be4039a5251ab4c848b0.png")
     msg=await ctx.send(embed=em)
     await msg.add_reaction("<:Serko:1216407871680544931>")

@client.command(aliases=['ro'])
async def rob(ctx,member : discord.Member):
    if ctx.channel.id == romid:
     await open_account(ctx.author)
     await open_account(member)
     if member == ctx.author:
     	msg=await ctx.send("**لا يمكنك سرقة نفسك.**")
     	await msg.add_reaction("<:Serko:1216407871680544931>")
     	return
     torob=await update_bank(ctx.author)
     if torob[0] < 1500:
     	msg=await ctx.send(f"**يجب ان يكون رصيدك 1500 على الأقل لسرقة {member.name}، رصيدك الحالي هو {torob[0]}**")
     	await msg.add_reaction("<:Serko:1216407871680544931>")
     	return
     bal = await update_bank(member)
     if bal[0]<100:
         msg=await ctx.send("**رصيدة اقل من 100**")
         await msg.add_reaction("<:Serko:1216407871680544931>")
         return
     earning = random.randint(500, 1000)
     await update_bank(ctx.author,earning)
     await update_bank(member,-1*earning)
     await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="سراق"))
     em=discord.Embed(description=f"**سرقت محفظة {member} وحصلت على {earning} سيركو**", color=ctx.author.color)
     em.set_thumbnail(url="https://fontmeme.com/permalink/240310/7f4de2c774f4be4039a5251ab4c848b0.png")
     msg=await ctx.send(embed=em)
     await msg.add_reaction("<:Serko:1216407871680544931>")

@client.command(aliases = ["t"])
async def top(ctx,x = 1):
    if ctx.channel.id == romid:
     users = await get_bank_data()
     leader_board = {}
     total = []
     for user in users:
         name = int(user)
         total_amount = users[user]["wallet"] + users[user]["bank"]
         leader_board[total_amount] = name
         total.append(total_amount)

     total = sorted(total,reverse=True)    

     em = discord.Embed(title=f"اغنى {x} اصحاب سيركو", color = discord.Color.orange())
     em.set_thumbnail(url="https://fontmeme.com/permalink/240310/7f4de2c774f4be4039a5251ab4c848b0.png")
     index = 1
     for amt in total:
         id_ = leader_board[amt]
         member = client.get_user(id_)
         name = member.name
         em.add_field(name = f"**{index} | {name} - {amt}**" , value = f"",  inline = False)
         if index == x:
             break
         else:
             index += 1

     msg=await ctx.send(embed=em)
     await msg.add_reaction("<:Serko:1216407871680544931>")

#----------------------------------------------------

async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open('mainbank.json','w') as f:
        json.dump(users,f)

    return True


async def get_bank_data():
    with open('mainbank.json','r') as f:
        users = json.load(f)

    return users


async def update_bank(user,change=0,mode = 'wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open('mainbank.json','w') as f:
        json.dump(users,f)
    bal = users[str(user.id)]['wallet'],users[str(user.id)]['bank']
    return bal

mainshop = [{"name":"عبد","price":100,"description":""},
            {"name":"Nerd","price":500,"description":""},
            {"name":"Rahan Wife","price":4000,"description":""},
            {"name":"سراق","price":5000,"description":""},
            {"name":"يقدر يشوف الارشيف","price":7000,"description":""}]

@client.command()
async def shop(ctx):
    em = discord.Embed(title = "الشوب", description=f"**للشراء: {prefix}buy اسم الرتبة**", color=discord.Color.random())
    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"**${price}  {desc}**")
        em.set_thumbnail(url=ctx.guild.icon)
    await ctx.send(embed = em)

async def buy_this(user,item_name):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower().encode("UTF-8")
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            break
        if t == None:
            obj = {"item":item_name}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]

@client.command()
async def buy(ctx,item):
 await open_account(ctx.author)
 res = await buy_this(ctx.author,item)
 if res[1]==2:
   await ctx.send(f"**لاتمتلك مال كافي لشراء {item}**")
   return
 await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name=item))
 await ctx.send(f"**مبروك، اشتريت رتبة {item}**")
 timestamp = datetime.datetime.now()
 users = await get_bank_data()
 walletnow= users[str(ctx.author.id)]["wallet"]
 banknow = users[str(ctx.author.id)]["bank"]
 channel = client.get_channel(1215703791232360519)
 buy=discord.Embed(title="**لوق الشراء**", description=f"""**
المشتري: {ctx.author.name}
الرتبة: {item}
رصيده الحالي: {walletnow} بالمحفظة، {banknow} بالبنك
وقت الشراء: {timestamp.strftime(r"%I:%M %p")}

إضافي:
تم الشراء بـ روم: {ctx.channel.name}

**""", color=discord.Color.orange())
 buy.set_thumbnail(url=ctx.guild.icon)
 await channel.send(embed=buy)

keep_alive()
client.run("OTQ0ODU0MTY5MTQ2MjQ5MjU3.GJUhRk.9MOh_2NU0k63ge4jCmDtQZY28WIhGF-_q2Koy8")
