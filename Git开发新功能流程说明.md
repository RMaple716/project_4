你好！欢迎来到 Git 的世界。作为第一次使用 Git 的新手，按照规范操作能帮你避免很多麻烦。

根据你提供的 `规范.md` 文件，我为你整理了一份**从零开始开发新功能的完整操作指南**，并补充了一些新手容易忽略的细节。

### 第一步：克隆项目 (Clone)
这是你已经知道的步骤。在终端（Terminal）或命令行中输入：
```bash
git clone <你的项目仓库地址>
cd preoject_4
```

### 第二步：初始化与配置 (Config)
在开始写代码前，先告诉 Git 你是谁。这很重要，因为提交记录会显示你的名字和邮箱。
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

### 第三步：确认当前状态
进入项目后，先看看自己在哪里，以及远程仓库有没有最新的变动。
```bash
git branch # 查看当前分支，通常会显示 * main
git pull origin main # 确保本地 main 分支是最新的
```

### 第四步：开发新功能 (Feature Branch)
**回答你的核心问题：** 是的，你需要新建分支。**永远不要直接在 `main` 分支上写代码**。

1. **创建并切换到新分支**：
   假设你要开发一个“用户登录”功能，根据规范，分支名应为 `feature/user-login`。
   ```bash
   git checkout -b feature/user-login
   ```
   *注：`-b` 的意思是“创建并切换”。*

2. **开始写代码**：
   现在你可以放心地在编辑器里修改、新增文件了。

3. **保存进度 (Add & Commit)**：
   当你完成了一小段逻辑（比如写好了登录页面的 UI），就把它存起来。
   ```bash
   git add . # 把所有改动的文件加入暂存区
   git commit -m "feat(auth): 完成登录页面UI布局" 
   ```
   *注：这里的 `-m` 后面跟着的是提交信息，请遵循规范中的格式 `<类型>: <描述>`。*

### 第五步：保持同步 (Sync)
如果你在开发过程中，队友已经往 `main` 分支合并了新代码，你需要把这些更新拉取到你的分支，防止最后合并时冲突太大。
```bash
# 1. 先切回主分支
git checkout main
# 2. 拉取最新代码
git pull origin main
# 3. 切回你的功能分支
git checkout feature/user-login
# 4. 把主分支的更新合并过来
git merge main
```
*如果这一步提示有冲突（Conflict），别慌，打开编辑器手动解决冲突后再提交即可。*

### 第六步：推送与提交流程 (Push & PR)
当你觉得功能开发完了：
1. **查看状态 (Status)**：
先看看你改了哪些文件，确保没有误删或遗漏。
```bash
git status
```
*如果显示红色文件名，说明这些文件被修改了但还没加入暂存区。*

2. **添加到暂存区 (Add)**：
把你改动的文件交给 Git 管理。如果你想提交所有改动：
```bash
git add .
```
*(注意：[.](file://d:\memberB\preoject_4\src\models\response.py) 代表当前目录下的所有变动)*

3. **提交到本地仓库 (Commit)**：
给这次改动写个备注，方便以后查找。根据规范，格式建议为 `类型: 描述`。
```bash
git commit -m "chore: 整理项目文档格式"
```
*例如：你只是修了个 Bug，可以写 `fix: 修复首页拼写错误`；如果是调整代码风格，可以写 `style: 统一代码缩进`。*

4. **推送到远程仓库**：
   ```bash
   git push origin feature/user-login
   ```

5. **发起 Pull Request (PR)**：
   去 GitHub/GitLab 网页端，你会看到提示让你创建一个 PR。
   - **标题**：简明扼要（如：`feat: 新增用户登录功能`）。
   - **描述**：写清楚你做了什么，怎么测试。
   - **请求审查**：邀请一位队友 Review 你的代码。

当队友在 GitHub 网页端审查（Review）并通过你的 Pull Request (PR) 后，合并操作通常有以下几种方式。根据你的项目规范（`规范.md`），推荐优先使用 **Squash and Merge**。


### 第七步：合并操作（当队友在 GitHub 网页端审查（Review）并通过你的 Pull Request (PR) 后）
### 方法一：在 GitHub 网页端合并（最推荐 ✅）

这是最简单且符合团队规范的方式。

1.  **找到合并按钮**：
    在你的 PR 页面底部，你会看到一个绿色的 **"Merge pull request"** 按钮。
2.  **选择合并策略**：
    点击按钮旁边的下拉箭头，根据 `规范.md` 第 3.3 节的要求，选择 **Squash and merge**。
    *   **Squash and merge**：会将你分支上的所有提交压缩成一个整洁的提交，然后合并到 [main](file://d:\memberB\preoject_4\test_task_decompose.py#L200-L215) 分支。这样可以保持 [main](file://d:\memberB\preoject_4\test_task_decompose.py#L200-L215) 分支的历史记录非常干净。
3.  **确认合并**：
    点击 **"Confirm squash and merge"**。
4.  **删除分支**：
    合并成功后，GitHub 会提示你 **"Delete branch"**。建议点击它，因为功能已经合并，这个临时分支就不再需要了。

### 方法二：在本地命令行合并（如果你需要在合并前做最后检查）

如果你想先在本地确认一切正常再合并，可以按以下步骤操作：

1.  **切换到主分支**：
    ```bash
    git checkout main
    ```
2.  **拉取最新代码**：
    ```bash
    git pull origin main
    ```
3.  **合并你的功能分支**：
    ```bash
    git merge --squash feature/Task_decomposition
    ```
    *注：`--squash` 参数对应网页端的 Squash 模式，它会把改动加进来但不自动提交，让你有机会写一个统一的提交信息。*
4.  **提交合并**：
    ```bash
    git commit -m "feat(task): 合并任务分解功能"
    ```
5.  **推送到远程**：
    ```bash
    git push origin main
    ```

### 💡 第八步：合并后的收尾工作

合并完成后，建议你清理一下本地的分支，保持环境整洁：

1.  **删除本地功能分支**：
    ```bash
    git branch -d feature/Task_decomposition
    ```
2.  **删除远程功能分支**（如果网页端没删）：
    ```bash
    git push origin --delete feature/Task_decomposition
    ```
3.  **同步主分支**：
    ```bash
    git pull origin main
    ```

### 💡 帮你考虑到的一些“新手坑”

1. **`.gitignore` 文件**：
   检查一下项目根目录有没有 `.gitignore` 文件。它的作用是告诉 Git **“哪些文件不需要上传”**（比如 `node_modules` 文件夹、系统生成的临时文件、包含密码的配置文件等）。如果没有这个文件，你可能会不小心把几百兆的依赖包传上去。

2. **提交粒度（Commit Granularity）**：
   规范里提到了“一次提交只做一件事”。
   - ❌ 错误做法：改了登录页，又顺手修了一个首页的 Bug，还删了几个没用的文件，最后一起提交。
   - ✅ 正确做法：分三次提交。这样如果后来发现登录页有问题，可以只撤销那一次提交，而不影响其他改动。

3. **遇到冲突怎么办？**
   如果你在执行 `git merge main` 或 `git pull` 时看到 "CONFLICT" 字样，说明你和别人改了同一个文件的同一行。
   - **建议**：先在本地用编辑器（VS Code 通常有可视化的解决冲突按钮）处理好，确认代码没问题了，再执行 `git add .` 和 `git commit`。

4. **善用 `git status`**：
   这是你最常用的命令。每做一步操作前，都可以输入 `git status` 看看：
   - 我现在在哪个分支？git statusgit status
   - 我改了哪些文件？
   - 哪些文件还没提交？

#### 1. 我什么都没改，只是想“同步”一下别人的代码怎么办？
如果你是想把队友写的最新代码拉取到你的电脑上，不需要 `push`，而是用 `pull`：
```bash
git pull origin main
```

#### 2. 为什么我执行 `git push` 时报错？
通常有几种可能：
*   **没登录/没权限**：检查你是否配置了 SSH Key 或账号密码。
*   **远程有更新**：如果队友刚提交了代码，你需要先 `git pull` 合并冲突，然后再 `git push`。
*   **分支不存在**：如果你是第一次推送一个新分支，Git 可能会提示你使用 `git push --set-upstream origin <分支名>`。

#### 3. “提交”和“推送”有什么区别？
*   **Commit (提交)**：是把代码保存到**你自己电脑**的 Git 历史记录里。即使断网也能做。
*   **Push (推送)**：是把你电脑上的记录**上传到服务器**（远程仓库），让队友能看到。

### 4. 当开发新功能时或新功能开发完成后，忘记开新分支怎么办

## 方法一：如果修改还未提交（推荐）

如果你只是修改了文件但还没有 commit，可以这样做：

```bash
# 1. 先暂存当前所有修改
git stash

# 2. 创建并切换到新分支
git checkout -b feature/integration-test-fix

# 3. 恢复之前的修改
git stash pop

# 4. 提交修改
git add .
git commit -m "fix: 修复行程整合测试边界情况返回值问题"
```

## 方法二：如果已经提交但未推送

如果你已经 commit 了但还没 push 到远程：

```bash
# 1. 创建新分支并指向当前提交
git branch feature/integration-test-fix

# 2. 回退当前分支（假设你在 main/master 分支）
git reset --hard HEAD~1  # 回退最后一个提交

# 3. 切换到新分支
git checkout feature/integration-test-fix

# 现在你的修改就在新分支上了
```

## 方法三：如果已经推送到远程

如果已经 push 了，需要更谨慎：

```bash
# 1. 基于当前提交创建新分支
git branch feature/integration-test-fix

# 2. 切换回原分支
git checkout main  # 或 master

# 3. 回退远程和本地的提交
git reset --hard HEAD~1
git push origin main --force  # 强制推送（如果其他人也在使用这个分支要小心）
```









