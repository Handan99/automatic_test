import pytest
from playwright.async_api import async_playwright
from pytest_asyncio import fixture as async_fixture

# todo_app项目链接：https://github.com/themaxsandelin/todo?tab=readme-ov-file

# 将打开浏览器的操作封装成固件函数
@async_fixture
async def browser_context():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        # 此处生成模拟浏览器上下文
        context = await browser.new_context()
        try:
            yield context
        finally:
            await context.close()
            await browser.close()
@async_fixture
async def page(browser_context):
    page = await browser_context.new_page()
    try:
        yield page
    finally:
        page.close()

# 添加待办事项
## 测试用例一：连续添加两个待办事项
@pytest.mark.asyncio
async def test_add_task_1(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入第一个待办事项的内容
    await page.fill("#item","第一个待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "第一个待办事项"

    # 输入第二个待办事项的内容
    await page.fill("#item","第二个待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 2
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "第二个待办事项"

## 测试用例二：输入框输入多种字符组合
@pytest.mark.asyncio
async def test_add_task_2(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入第一个待办事项的内容
    await page.fill("#item","12345abcdefgABCDEFG!@#$%^&*()_+")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "12345abcdefgABCDEFG!@#$%^&*()_+"

## 测试用例三：输入框图片无法粘贴
@pytest.mark.asyncio
async def test_add_task_3(page):
    # 打开一张图片地址并复制到剪切板
    await page.goto("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png")
    # 使用 src 属性选择图片
    image = page.locator('img[src="https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"]')
    await image.click(button="left")
    await page.keyboard.press("Control+C")
    # 打开待办事项应用粘贴图片到输入框
    await page.goto("http://localhost:3000")
    input_box = page.locator("#item")
    await input_box.click(button="left")
    await page.keyboard.press("Control+V")
    # 判断当前输入框是否为空
    assert await page.locator("#item").input_value() == ""

## 测试用例四：输入框为空
@pytest.mark.asyncio
async def test_add_task_4(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 0
    # 判断输入框是否为空
    assert await page.locator("#item").input_value() == ""

## 测试用例五：输入框超出内容长度
### 原代码未规定输入长度，在index.html第22行标签中添加 maxlength="50" 属性
@pytest.mark.asyncio
async def test_add_task_5(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入超过长度限制的待办事项内容
    await page.fill("#item", 'a' * 51)
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    input_text = await page.locator("#todo").locator("li").nth(0).inner_text()
    assert len(input_text) == 50

## 测试用例六：输入已存在的待办事项的内容
@pytest.mark.asyncio
async def test_add_task_6(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入第一个待办事项的内容
    await page.fill("#item","测试重复待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "测试重复待办事项"

    # 输入第二个待办事项的内容
    await page.fill("#item","测试重复待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 2
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "测试重复待办事项"

# 删除待办事项
## 测试用例一：删除已完成待办事项
@pytest.mark.asyncio
async def test_delete_task_1(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入第一个待办事项的内容
    await page.fill("#item","测试删除待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "测试删除待办事项"

    # 点击已完成
    selector_com = page.locator("#todo").locator("li").nth(0).locator(".complete")
    await selector_com.click()
    # 判断未完成事项个数
    assert await page.locator("#todo").locator("li").count() == 0
    # 判断已完成事项个数
    assert await page.locator("#completed").locator("li").count() == 1

    # 点击删除
    selector_rem = page.locator("#completed").locator("li").nth(0).locator(".remove")
    await selector_rem.click()
    # 判断已完成事项个数
    assert await page.locator("#completed").locator("li").count() == 0

## 测试用例二：删除未完成待办事项
@pytest.mark.asyncio
async def test_delete_task_2(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入第一个待办事项的内容
    await page.fill("#item","测试删除待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "测试删除待办事项"

    # 点击删除
    selector_rem = page.locator("#todo").locator("li").nth(0).locator(".remove")
    await selector_rem.click()
    # 判断未完成事项个数
    assert await page.locator("#todo").locator("li").count() == 0

# 完成待办事项
## 测试用例一：完成待办事项
@pytest.mark.asyncio
async def test_complete_task_1(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入第一个待办事项的内容
    await page.fill("#item","测试删除待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "测试删除待办事项"

    # 点击已完成
    selector_com = page.locator("#todo").locator("li").nth(0).locator(".complete")
    await selector_com.click()
    # 判断未完成事项个数
    assert await page.locator("#todo").locator("li").count() == 0
    # 判断已完成事项个数
    assert await page.locator("#completed").locator("li").count() == 1

## 测试用例二：完成后取消完成
@pytest.mark.asyncio
async def test_complete_task_2(page):
    # 打开待办事项应用
    await page.goto("http://localhost:3000")
    # 输入第一个待办事项的内容
    await page.fill("#item","测试删除待办事项")
    # 点击添加按钮
    await page.click("#add")
    # 判断是否添加成功
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断添加内容是否正确
    assert await page.locator("#todo").locator("li").nth(0).inner_text() == "测试删除待办事项"

    # 点击已完成
    selector_com = page.locator("#todo").locator("li").nth(0).locator(".complete")
    await selector_com.click()
    # 判断未完成事项个数
    assert await page.locator("#todo").locator("li").count() == 0
    # 判断已完成事项个数
    assert await page.locator("#completed").locator("li").count() == 1

    # 点击取消已完成
    selector_com = page.locator("#completed").locator("li").nth(0).locator(".complete")
    await selector_com.click()
    # 判断未完成事项个数
    assert await page.locator("#todo").locator("li").count() == 1
    # 判断已完成事项个数
    assert await page.locator("#completed").locator("li").count() == 0

