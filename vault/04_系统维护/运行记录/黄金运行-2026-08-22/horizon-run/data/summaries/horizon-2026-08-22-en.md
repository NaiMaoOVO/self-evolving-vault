# Horizon Daily - 2026-08-22

> From 43 items, 22 important content pieces were selected

---

**Technology News**
1. [Roblox Open-Sources Three AI Safety Models](#item-tech-news-1) ⭐️ 7.0/10
2. [llm-openrouter 0.7 adds LLM 0.32 support and new tools](#item-tech-news-2) ⭐️ 6.0/10
3. [Stop Making TUIs: Build Native UIs with AI Agents](#item-tech-news-3) ⭐️ 6.0/10
4. [Matt Webb Uses ChatGPT as Tutor to Learn Quaternions for AR App](#item-tech-news-4) ⭐️ 6.0/10
5. [Spellcaster：让一个不会写代码的人，用AI把脑子里的游戏做出来了](#item-tech-news-5) ⭐️ 6.0/10
6. [LLM 0.32.1 Fixes Broken Dependency on httpx](#item-tech-news-6) ⭐️ 5.0/10
7. [Metal Gear Solid: Master Collection Vol.2 Preview](#item-tech-news-7) ⭐️ 5.0/10
8. [Sony&\#x27;s Live Service Pivot: A Costly Misstep](#item-tech-news-8) ⭐️ 5.0/10
9. [Merge Game Market: Chinese Publishers Dominate with $99M Monthly Revenue](#item-tech-news-9) ⭐️ 5.0/10
10. [Double Fine retains IP and publishing rights after Xbox split](#item-tech-news-10) ⭐️ 5.0/10
11. [No Man&\#x27;s Sky&\#x27;s Galactic Hub: A Decade of Utopia](#item-tech-news-11) ⭐️ 5.0/10
12. [Cicadamata: A Striking New FPS Platformer Released](#item-tech-news-12) ⭐️ 5.0/10
13. [Sandustry Review: A Factory Builder That Gets It Right](#item-tech-news-13) ⭐️ 5.0/10
14. [Compulsion Games Regains Rights After Leaving Xbox](#item-tech-news-14) ⭐️ 5.0/10
15. [Avoid Fake GTA 6 Leak Downloads to Prevent Malware](#item-tech-news-15) ⭐️ 5.0/10
16. [Xbox Console Ads Could Benefit Gaming](#item-tech-news-16) ⭐️ 4.0/10
17. [Zenless Zone Zero Lead Artist Leaves miHoYo for Indie Farming Game](#item-tech-news-17) ⭐️ 4.0/10
18. [NetEase Q2 2026: Game Revenue 25B RMB, New Titles in Testing](#item-tech-news-18) ⭐️ 4.0/10
19. [Take-Two subpoenas Microsoft and Discord to unmask GTA 6 leaker](#item-tech-news-19) ⭐️ 4.0/10
20. [Plague Tale Resonance Leaks Online Ahead of Launch](#item-tech-news-20) ⭐️ 4.0/10
21. [Cyberpunk: Edgerunners 2 Premieres October 20](#item-tech-news-21) ⭐️ 4.0/10
22. [Among Shadows Preview: Dark Fantasy RPG with Social Deduction](#item-tech-news-22) ⭐️ 4.0/10

---

## Technology News

<a id="item-tech-news-1"></a>
### [Roblox Open-Sources Three AI Safety Models](https://www.gamesindustry.biz/roblox-makes-three-of-its-ai-safety-tools-open-source) ⭐️ 7.0/10

Roblox has open-sourced three of its AI safety models through the Robust Open Online Safety Tools \(ROOST\) Model Community, an initiative aimed at improving online safety tools. The announcement, made via Roblox&\#x27;s newsroom in August 2026, marks a significant step in sharing moderation technology with the broader community. The specific models have not been detailed in the available source, but the move is intended to help developers and platforms enhance their content moderation capabilities. This open-sourcing effort reflects Roblox&\#x27;s commitment to collaborative safety solutions in the gaming and online interaction space.

rss · GamesIndustry.biz · Aug 21, 10:35

**「Background」** ROOST \(Robust Open Online Safety Tools\) is a collaborative initiative that provides open-source tools and models to help online platforms improve safety and moderation. Roblox has previously contributed to this community, and its latest contribution includes an updated PII Classifier, Roblox Sentinel, and a new voice safety classifier, along with an evaluation dataset for benchmarking.

**「Impact」** Developers and online platforms can now access and integrate Roblox&\#x27;s AI safety models to strengthen their own content moderation systems, potentially improving safety across the industry.

<details><summary>References</summary>
<ul>
<li><a href="https://about.roblox.com/newsroom/2026/08/roblox-open-source-safety-models-roost">Roblox Brings Open-Source Safety Models to ROOST Model Community | Roblox</a></li>

</ul>
</details>

**Tags**: `#AI safety`, `#open source`, `#content moderation`, `#Roblox`, `#online safety`

---

<a id="item-tech-news-2"></a>
### [llm-openrouter 0.7 adds LLM 0.32 support and new tools](https://simonwillison.net/2026/Aug/21/llm-openrouter/) ⭐️ 6.0/10

llm-openrouter 0.7 is a new release of the plugin that integrates OpenRouter with the LLM command-line tool. It adds compatibility with LLM 0.32, enabling the display of reasoning traces for models accessed through OpenRouter. The plugin now uses OpenRouter&\#x27;s implementation of the Responses API for model interactions. It also introduces three new server-side tools: Shell, WebFetch, and WebSearch, which can be enabled with options like \`-T WebSearch\`. This update is incremental but useful for developers using LLM with OpenRouter.

rss · Simon Willison · Aug 21, 16:58

**「Background」** LLM is a command-line tool for interacting with various large language models, and OpenRouter is a service that provides access to multiple models through a unified API. The llm-openrouter plugin allows LLM users to leverage OpenRouter&\#x27;s model offerings. LLM 0.32 introduced support for reasoning traces, which show the model&\#x27;s internal reasoning process, and this plugin update ensures compatibility with that feature.

**「Impact」** Developers using LLM with OpenRouter can now see reasoning traces for supported models and use new server-side tools like WebSearch, enhancing their ability to build and debug AI-powered workflows.

**Tags**: `#LLM`, `#OpenRouter`, `#plugin`, `#AI tools`, `#release`

---

<a id="item-tech-news-3"></a>
### [Stop Making TUIs: Build Native UIs with AI Agents](https://simonwillison.net/2026/Aug/21/stop-making-tuis/) ⭐️ 6.0/10

Thomas Ptacek argues that developers should build native user interfaces for even the smallest personal tools, because AI coding agents have drastically reduced the cost of creating a usable GUI. Simon Willison highlights this post, noting that he has been using two vibe-coded macOS task bar apps for bandwidth and GPU monitoring since March 2026. Willison admits he hasn&\#x27;t yet converted all his throwaway CLIs into native apps but sees fewer excuses to avoid doing so. Ptacek encourages developers to try turning one of their many CLI tools into a native app, suggesting it will change their perspective. The discussion reflects a broader trend in developer tooling toward AI-assisted UI development.

rss · Simon Willison · Aug 21, 16:07

**「Background」** Thomas Ptacek is a well-known security researcher and co-founder of Matasano Security, which later became part of NCC Group. In his blog post &\#x27;Stop Making TUIs,&\#x27; he argues that AI coding agents have made it cheap and easy to build native graphical user interfaces \(GUIs\) for small personal tools, so developers should move beyond text-based command-line interfaces \(CLIs\) and terminal user interfaces \(TUIs\). Simon Willison, a prominent developer and blogger, echoes this sentiment, noting that he has already used &\#x27;vibe coding&\#x27; to create macOS task bar apps for bandwidth and GPU monitoring, which he uses daily.

**「Impact」** Developers who adopt AI coding agents may find it practical to create native UIs for small tools, potentially improving usability and accessibility of personal utilities. This shift could lead to a broader move away from CLI-only tools in favor of more intuitive interfaces.

<details><summary>References</summary>
<ul>
<li><a href="https://simonwillison.net/2026/Aug/21/stop-making-tuis/">Stop Making TUIs | Simon Willison’s Weblog</a></li>
<li><a href="https://blackhat.com/us-14/speakers/Thomas-Ptacek.html">Black Hat USA 2014 | Thomas Ptacek</a></li>

</ul>
</details>

**Tags**: `#AI-assisted development`, `#native UI`, `#developer tools`, `#vibe coding`, `#software engineering`

---

<a id="item-tech-news-4"></a>
### [Matt Webb Uses ChatGPT as Tutor to Learn Quaternions for AR App](https://simonwillison.net/2026/Aug/21/matt-webb/) ⭐️ 6.0/10

Matt Webb, creator of the Galactic Compass app, shared that after releasing version 1.0, he used ChatGPT as an interactive tutor to learn quaternions—a mathematical concept needed for rotations in his app&\#x27;s new augmented reality mode. Instead of having the AI write code, he asked it to educate him, which enabled him to finally grasp quaternions after failing with books and mathematician friends. Webb emphasizes that outsourcing thinking to AI did not stop his learning but pushed him to learn more, highlighting a positive outcome of AI-assisted education. The quote was published on his blog and reposted by Simon Willison, underscoring the growing role of generative AI in personalized learning.

rss · Simon Willison · Aug 21, 15:06

**「Background」** Quaternions are a number system used in 3D graphics and augmented reality to represent rotations, but they are notoriously difficult to understand. Matt Webb&\#x27;s Galactic Compass is an app that likely uses AR to overlay directional information, requiring precise rotation calculations. His anecdote illustrates a broader trend where AI chatbots like ChatGPT are used not just for code generation but as patient, interactive tutors for complex topics.

**「Impact」** This anecdote suggests that AI tools can effectively bridge gaps in technical education, enabling developers to acquire specialized knowledge on demand, which may accelerate innovation in fields like AR. It also implies a shift in how professionals approach learning, using AI as a supplement rather than a replacement for understanding.

**Tags**: `#AI-assisted learning`, `#ChatGPT`, `#augmented reality`, `#quaternions`, `#generative AI`

---

<a id="item-tech-news-5"></a>
### [Spellcaster：让一个不会写代码的人，用AI把脑子里的游戏做出来了](https://www.youxituoluo.com/534815.html) ⭐️ 6.0/10

Spellcaster lets non-coders turn game ideas into playable prototypes, as shown by a game designer who created a nuclear tank game.

rss · 游戏陀螺 · Aug 21, 09:57

**Tags**: `#AI game development`, `#no-code tools`, `#game prototyping`, `#generative AI`, `#game design`

---

<a id="item-tech-news-6"></a>
### [LLM 0.32.1 Fixes Broken Dependency on httpx](https://simonwillison.net/2026/Aug/21/llm/) ⭐️ 5.0/10

LLM 0.32.1, a patch release of Simon Willison&\#x27;s command-line tool for interacting with large language models, fixes a dependency issue that broke fresh installs. The OpenAI Python library recently dropped its usage of httpx, and LLM relied on httpx only as a transitive dependency of openai, causing installation failures. This release pins openai&lt;3 to restore functionality temporarily, while an upcoming 0.33 release will migrate from httpx to httpx2. The fix is relevant for developers using LLM, ensuring the tool installs and runs correctly again.

rss · Simon Willison · Aug 21, 17:16

**「Background」** LLM is a command-line tool that provides a unified interface for interacting with various large language models, including those from OpenAI. It depends on the OpenAI Python library, which historically used the httpx HTTP client library. When OpenAI removed httpx from its dependencies, LLM&\#x27;s transitive dependency on httpx was lost, breaking installations.

**「Impact」** Developers who install LLM fresh will now be able to install and use it again, thanks to the pinning of openai&lt;3. The upcoming 0.33 release will provide a more permanent solution by switching to httpx2.

**Tags**: `#LLM`, `#OpenAI`, `#httpx`, `#dependency`, `#release`

---

<a id="item-tech-news-7"></a>
### [Metal Gear Solid: Master Collection Vol.2 Preview](https://www.gcores.com/articles/218638) ⭐️ 5.0/10

Metal Gear Solid: Master Collection Vol.2 will be released on August 27, featuring Metal Gear Solid 4: Guns of the Patriots, Metal Gear Solid: Peace Walker, and Metal Gear Solid: Ghost Babel as a bonus. The highlight is MGS4&\#x27;s first release on PC and modern consoles after being a PS3 exclusive since 2008. The collection supports up to 4K resolution and 60 fps on PS5, Xbox Series X, and PC, with the 60 fps noted as a variable maximum. The preview build showed stable 60 fps on an RTX 4060 at 2K resolution, though Peace Walker exhibited frame drops in an early beach training level. The collection lacks Chinese language support, and MGS4&\#x27;s Japanese save data is not interchangeable with other language versions.

rss · 机核gcores · Aug 21, 10:20

**「Background」** The Metal Gear Solid series, created by Hideo Kojima, is known for its stealth gameplay and cinematic storytelling. MGS4 concluded Solid Snake&\#x27;s story and was a technical showcase for the PS3, earning perfect scores from Famitsu. Peace Walker, originally a PSP title, bridged the story between MGS3 and MGS5, and Ghost Babel is a non-canonical Game Boy Color spin-off. The Master Collection series aims to bring classic titles to modern platforms.

**「Impact」** This release finally makes MGS4 accessible to PC and modern console players, ending its long-standing platform exclusivity, and provides a definitive way to experience key entries in the series with improved performance and visual fidelity.

**Tags**: `#gaming`, `#metal-gear-solid`, `#game-collection`, `#pc-gaming`, `#konami`

---

<a id="item-tech-news-8"></a>
### [Sony&\#x27;s Live Service Pivot: A Costly Misstep](https://www.gamesindustry.biz/the-opportunity-cost-of-sonys-live-service-pivot-is-enormous-opinion) ⭐️ 5.0/10

An opinion piece by Rob Fahey on GamesIndustry.biz argues that Sony&\#x27;s pivot to live service games has incurred enormous opportunity costs. The article contends that the industry-wide live service mania, which consumed vast financial resources and labor, has also eroded consumer goodwill and IP value. It highlights the strategic missteps of assuming every game could or should be a live service title. The piece underscores the significant trade-offs Sony made in pursuing this direction, potentially at the expense of other opportunities.

rss · GamesIndustry.biz · Aug 21, 14:15

**「Background」** The live service model refers to games that are continuously updated with new content and monetization, often featuring microtransactions and seasonal content. Over the past decade, many publishers, including Sony, shifted focus toward this model, hoping to replicate the success of titles like Fortnite. This pivot often came at the cost of single-player, narrative-driven games, which have traditionally been a strength for Sony.

**「Impact」** Sony&\#x27;s focus on live service games may have diverted resources from its acclaimed single-player franchises, potentially affecting its portfolio and consumer trust. The long-term financial and reputational consequences remain uncertain, but the opportunity cost is significant.

**Tags**: `#gaming industry`, `#business strategy`, `#Sony`, `#live service`, `#opinion`

---

<a id="item-tech-news-9"></a>
### [Merge Game Market: Chinese Publishers Dominate with $99M Monthly Revenue](https://www.youxituoluo.com/534817.html) ⭐️ 5.0/10

According to Sensor Tower&\#x27;s 2026 H1 merge game trend report, global in-app purchase revenue for merge games exceeded $2.1 billion in the first half of 2026, up 34% year-over-year, with two-merge gameplay accounting for 96% of downloads and 93% of revenue. Chinese publishers dominate the market, led by Lemon Micro and Diandian Interactive. Lemon Micro&\#x27;s top title Gossip Harbor: Merge &amp; Story earned $99 million in July 2026 alone, while its other two titles each brought in $14 million, totaling nearly $130 million. Diandian Interactive&\#x27;s Tasty Travels: Merge Game generated $29 million in July, with new titles like Hotel Legacy earning $2.8 million. Other notable performers include Tian Tian Wan Jia&\#x27;s Merge Cooking at $13 million, Lexin Shengwen&\#x27;s Mystery Town at $10 million, and VoyagerOne&\#x27;s Hollywood Merge at $8 million. The market is highly concentrated, with top products earning tens of millions monthly, while newcomers aim to break through with genre innovation and IP collaborations.

rss · 游戏陀螺 · Aug 21, 14:16

**「Background」** Merge games are a mobile puzzle subgenre where players combine items to create higher-level objects, often to complete orders or progress a story. According to Sensor Tower&\#x27;s 2026 mid-year report, global merge game revenue exceeded $2.1 billion in the first half of 2026, making it the second-largest puzzle subcategory, with two-merge \(merge-two\) mechanics dominating at over 90% of downloads and revenue. This growth has attracted major Chinese publishers, who now lead the market with top titles earning tens of millions monthly.

**「Impact」** The dominance of Chinese publishers in the merge game market, with top titles earning tens of millions monthly, raises the barrier to entry for new competitors, forcing them to innovate in themes and gameplay to capture niche audiences.

<details><summary>References</summary>
<ul>
<li><a href="https://news.qq.com/rain/a/20260804A06F6Z00">Sensor Tower ：2026上半年全球合成手游收入突破21亿美元 二合手游贡...</a></li>
<li><a href="https://www.msn.cn/zh-cn/news/other/sensor-tower%E6%8A%A5%E5%91%8A-2026%E4%B8%8A%E5%8D%8A%E5%B9%B4%E5%85%A8%E7%90%83%E5%90%88%E6%88%90%E6%89%8B%E6%B8%B8%E5%90%B8%E9%87%91%E8%B6%8521%E4%BA%BF%E7%BE%8E%E5%85%83-%E4%BA%8C%E5%90%88%E7%8E%A9%E6%B3%95%E6%88%90%E4%B8%BB%E5%8A%9B/ar-AA29neGc">Sensor Tower报告：2026上半年全球合成手游吸金超21亿美元 二合玩法成...</a></li>
<li><a href="https://www.sohu.com/a/1058676064_121814834">Sensor Tower：2026上半年全球合成手游收入突破21亿美元 二合手游贡献...</a></li>

</ul>
</details>

**Tags**: `#mobile gaming`, `#market analysis`, `#merge games`, `#Sensor Tower`, `#game industry`

---

<a id="item-tech-news-10"></a>
### [Double Fine retains IP and publishing rights after Xbox split](https://www.eurogamer.net/double-fine-ip-publishing-rights-xbox-split) ⭐️ 5.0/10

Double Fine has confirmed that it owns, or will shortly own, the intellectual property and publishing rights to every game it made during its seven years under Xbox, following the studio&\#x27;s split from Microsoft earlier this year. This means the studio retains control over titles developed during that period, including Psychonauts 2 and other franchises. The confirmation clarifies the studio&\#x27;s independence and its ability to manage its catalog without Microsoft&\#x27;s involvement. This development is significant for the gaming industry as it highlights a shift in studio-publisher relationships and the value of IP ownership.

rss · Eurogamer · Aug 22, 10:33

**「Background」** Double Fine was acquired by Microsoft in 2019 and operated under Xbox Game Studios for seven years. During that time, it developed games such as Psychonauts 2. The split from Microsoft earlier this year raised questions about the ownership of the studio&\#x27;s IP and publishing rights, which have now been clarified.

**「Impact」** Double Fine&\#x27;s retention of its IP and publishing rights ensures that the studio can independently manage, re-release, or license its games without Microsoft&\#x27;s approval, which is a concrete benefit for the studio and its fans. This may also set a precedent for other studios leaving major publishers, though the specifics of each deal vary.

**Tags**: `#gaming`, `#intellectual-property`, `#xbox`, `#double-fine`, `#industry-news`

---

<a id="item-tech-news-11"></a>
### [No Man&\#x27;s Sky&\#x27;s Galactic Hub: A Decade of Utopia](https://www.eurogamer.net/no-mans-sky-players-building-utopia-optimism-week) ⭐️ 5.0/10

The Galactic Hub Project in No Man&\#x27;s Sky has grown into a thriving, player-built community over the past decade, spanning three galaxies and thousands of star systems. Founded during a period of low positivity, the project combines scientific exploration with social collaboration, creating a utopian society in a universe that is perpetually 16 minutes from destruction. The community continues to expand, showcasing the enduring appeal of cooperative play and shared goals in the game. This feature highlights the project&\#x27;s role as a testament to player-driven creativity and kindness within the No Man&\#x27;s Sky universe.

rss · Eurogamer · Aug 21, 12:15

**「Background」** No Man&\#x27;s Sky is a procedurally generated space exploration game where players can discover and name planets, build bases, and interact with others. The Galactic Hub Project is a player-organized initiative that establishes a central hub for players to collaborate, share discoveries, and build communities. It was founded in 2016, shortly after the game&\#x27;s launch, as a way to foster a positive and organized player base.

**「Impact」** The Galactic Hub Project demonstrates the potential for long-term, player-driven communities in open-world games, influencing how developers and players approach cooperative gameplay and social features. Its decade-long success provides a model for community building in procedurally generated environments.

**Tags**: `#gaming`, `#community`, `#No Man&\#x27;s Sky`

---

<a id="item-tech-news-12"></a>
### [Cicadamata: A Striking New FPS Platformer Released](https://www.rockpapershotgun.com/indecently-cool-fps-platformer-cicadamata-is-out-now-please-get-yourself-down-that-rabbit-hole) ⭐️ 5.0/10

Cicadamata, a visually striking FPS platformer from developer flowergarden, has been released, as announced by Rock Paper Shotgun. The game is described as a &\#x27;movement shooter&\#x27; with a distinctive aesthetic that the article&\#x27;s author struggles to capture in words, comparing it to surreal experiences like &\#x27;drinking the aurora borealis&\#x27; or &\#x27;surfing the Niagara Falls during a freak shower of potassium pellets.&\#x27; The article primarily highlights the game&\#x27;s sensory impact and encourages readers to explore it, but provides limited technical details or performance specifics. The release marks the availability of this indie title, which blends first-person shooting with platforming mechanics.

rss · Rock Paper Shotgun · Aug 21, 18:35

**「Background」** Cicadamata is an indie game in the FPS platformer genre, often referred to as &\#x27;movement shooters,&\#x27; which emphasize agility and acrobatic traversal alongside combat. The developer, flowergarden, is known for creating games with unconventional aesthetics and gameplay, though specific prior works are not detailed in the source. The game&\#x27;s title includes unusual punctuation, reflecting its quirky style.

**「Impact」** The release of Cicadamata adds a new option for fans of indie FPS platformers seeking visually distinctive and movement-focused experiences, though its broader impact on the gaming landscape remains to be seen given the lack of detailed technical or commercial data.

**Tags**: `#game release`, `#FPS`, `#platformer`, `#indie game`

---

<a id="item-tech-news-13"></a>
### [Sandustry Review: A Factory Builder That Gets It Right](https://www.rockpapershotgun.com/sandustry-is-the-first-factory-simulation-game-ive-played-that-gets-heaps-right) ⭐️ 5.0/10

Sandustry, a new spelunking factory builder from Lantto Games and Hooded Horse, is praised by Rock Paper Shotgun&\#x27;s Edwin Evans-Thirlwell as the first factory simulation game that gets many things right. The review highlights the game&\#x27;s unique setting in underground caves and its innovative approach to the genre, though specific mechanics are not detailed in the excerpt. The article also draws a comparison to the post-industrial slate quarries of Wales, setting a thematic tone. The review is positive, suggesting Sandustry stands out among building games on PC.

rss · Rock Paper Shotgun · Aug 21, 17:00

**「Background」** Sandustry is an automation, exploration, and base-building strategy game developed by Lantto Games and published by Hooded Horse. It features fully destructible worlds where players mine resources and automate increasingly complex production chains, with a release date of August 13, 2026. The game has gained attention on Steam as a small factory game that has become popular.

**「Impact」** For fans of factory simulation and building games, Sandustry may offer a fresh and compelling experience that addresses common genre pitfalls, potentially influencing future game design trends.

<details><summary>References</summary>
<ul>
<li><a href="https://wiki.hoodedhorse.com/Sandustry/Sandustry_Official_Wiki">Sandustry Official Wiki - Sandustry Official Wiki</a></li>
<li><a href="https://www.hoodedhorse.com/games/sandustry">Sandustry | Hooded Horse</a></li>
<li><a href="https://www.dlcompare.com/gaming-news/sandustry-is-the-tiny-factory-game-blowing-up-on-steam">Sandustry is the tiny factory game blowing up on Steam</a></li>

</ul>
</details>

**Tags**: `#game review`, `#factory simulation`, `#Sandustry`, `#building games`, `#PC gaming`

---

<a id="item-tech-news-14"></a>
### [Compulsion Games Regains Rights After Leaving Xbox](https://www.rockpapershotgun.com/were-going-to-take-things-slow-south-of-midnight-devs-now-own-the-rights-to-all-their-games-again-after-quitting-xbox-and-are-working-on-a-new-game) ⭐️ 5.0/10

Compulsion Games, the developer behind We Happy Few and South of Midnight, has completed a management buyout and is now fully independent from Microsoft and Xbox. The studio has regained the rights to all its original intellectual properties, meaning that purchases of the Steam version of South of Midnight now go directly to Compulsion \(after Valve&\#x27;s revenue cut\). The team is currently working on a new game, and the studio&\#x27;s leadership emphasized a cautious approach, stating they are going to take things slow. This separation also allows players to support the studio without conflicting with the BDS boycott against Microsoft&\#x27;s Israeli military connections.

rss · Rock Paper Shotgun · Aug 21, 10:25

**「Background」** Compulsion Games, the Canadian studio behind We Happy Few and South of Midnight, was acquired by Microsoft in 2018 and operated as a first-party Xbox studio. On July 6, 2026, the studio announced its split from Xbox, and by August 11, 2026, it completed a management buyout, regaining full rights to its original intellectual properties and becoming independent again.

**「Impact」** For players and fans, buying South of Midnight on Steam now directly supports Compulsion Games financially, and the studio&\#x27;s independence may influence its future creative direction and project choices.

<details><summary>References</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Compulsion_Games">Compulsion Games - Wikipedia</a></li>

</ul>
</details>

**Tags**: `#gaming industry`, `#studio independence`, `#Microsoft`, `#Compulsion Games`, `#IP rights`

---

<a id="item-tech-news-15"></a>
### [Avoid Fake GTA 6 Leak Downloads to Prevent Malware](https://www.rockpapershotgun.com/psa-in-the-latest-gta-6-leaks-aftermath-its-not-a-good-idea-to-download-files-with-names-like-totallylegitgta6leakedbuildexe) ⭐️ 5.0/10

Following the latest GTA 6 leak, cybersecurity experts warn that downloading files claiming to be leaked builds of the game, such as those with names like &\#x27;totallylegitgta6leakedbuild.exe&\#x27;, is risky and could lead to malware infections. This uptick in malicious activity is attributed to scammers exploiting the hype around the leak, which was reportedly carried out by a group called Cyberleek. While such scams are not new, the recent leak has intensified the danger. Users are advised to avoid downloading any files that purport to be GTA 6 content, as they may contain harmful software.

rss · Rock Paper Shotgun · Aug 21, 09:31

**「Background」** GTA 6 is one of the most anticipated video games, and its development has been plagued by leaks. In 2022, a major leak exposed early gameplay footage, and in September 2024, a new leak emerged from a hacker group called Cyberleek, who claimed to have access to a playable build of the game. This has led to a surge in fake files and malware disguised as GTA 6 leaks, as cybercriminals exploit the hype to trick users into downloading malicious software.

**「Impact」** Gamers eager to access leaked GTA 6 content are at an increased risk of malware infections, which could compromise their personal data and device security. This warning is particularly relevant for those who might be tempted to download unofficial files following the leak.

<details><summary>References</summary>
<ul>
<li><a href="https://news.google.com/stories/CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2ljNTlEb0VSRmlsN3k0eENQcjJ5Z0FQAQ?hl=en-US&amp;gl=US&amp;ceid=US:en">Google News - News about GTA 6 - Overview</a></li>
<li><a href="https://www.techspot.com/news/113566-gta-6-leaker-may-have-access-playable-build.html">GTA 6 leaker may have access to a playable build as fake... | TechSpot</a></li>

</ul>
</details>

**Tags**: `#cybersecurity`, `#malware`, `#GTA 6`, `#gaming`, `#scams`

---

<a id="item-tech-news-16"></a>
### [Xbox Console Ads Could Benefit Gaming](https://www.gamesindustry.biz/why-xboxs-console-ads-could-be-a-good-thing-for-gaming-opinion) ⭐️ 4.0/10

In an opinion piece for GamesIndustry.biz, Virginie Chesnais, CMO of ad tech analytics platform Happydemics, argues that Xbox&\#x27;s console ads could be a positive development for the gaming industry. She suggests that such advertising can help expand the gaming audience and provide new revenue streams for developers and publishers. The piece emphasizes the potential for ads to be integrated in a way that enhances rather than disrupts the gaming experience. However, it is an opinion piece from a marketing executive, so it lacks technical depth and may be promotional in nature.

rss · GamesIndustry.biz · Aug 21, 11:00

**「Background」** Xbox has been exploring advertising on its console platform, which has sparked debate within the gaming community. Historically, console gaming has been largely ad-free, with revenue coming from game sales and subscriptions. The introduction of ads could represent a shift in the business model, potentially lowering costs for consumers or providing new monetization opportunities for developers.

**「Impact」** If implemented thoughtfully, Xbox console ads could provide developers and publishers with additional revenue, potentially leading to lower game prices or more free-to-play content, but the actual impact depends on execution and user acceptance.

**Tags**: `#gaming`, `#advertising`, `#opinion`, `#Xbox`

---

<a id="item-tech-news-17"></a>
### [Zenless Zone Zero Lead Artist Leaves miHoYo for Indie Farming Game](https://www.youxituoluo.com/534818.html) ⭐️ 4.0/10

On August 20, the lead artist of Zenless Zone Zero, known as &quot;Atu Friend&quot; \(阿兔朋友\), announced on Bilibili that they have left miHoYo. Atu Friend was responsible for designing many notable characters in the game, including Von Lycaon, Ellen Joe, Hoshimi Miyabi, Billy Kid, and Trigger. In their post, they reflected on the project&\#x27;s growth from a team of about 20 people to its current scale. After leaving miHoYo, they plan to develop an independent farming simulation game, a genre they have enjoyed for nearly 20 years, from Harvest Moon in their student days to recent titles like Silent Fields. The game is still in early development, and they are currently seeking initial team members. Zenless Zone Zero producer Li Zhenyu has expressed support and provided encouragement and advice.

rss · 游戏陀螺 · Aug 21, 14:54

**「Background」** Zenless Zone Zero is an action role-playing game developed by miHoYo \(now HoYoverse\), released in 2024. The game&\#x27;s lead artist, known as &quot;A Tu Pengyou&quot; \(阿兔朋友\), had been with the project for about six years and contributed to the design of several notable characters, including Von Lycaon, Ellen Joe, Hoshimi Miyabi, Billy Kid, and Trigger. The artist announced their departure from miHoYo on August 20, 2026, via Bilibili, and revealed plans to develop an independent farming simulation game, a genre they have enjoyed since playing Harvest Moon in their student days.

**「Impact」** The departure of a key artist may affect the artistic direction of Zenless Zone Zero&\#x27;s future character designs, while the indie farming game could bring a fresh perspective to the genre, though it is too early to assess its potential impact.

<details><summary>References</summary>
<ul>
<li><a href="https://www.ali213.net/news/html/2026-8/1033097.html">ali213.net/news/html/2026-8/1033097.html</a></li>
<li><a href="https://www.3dmgame.com/news/202608/3951103.html">曝《 绝 区 零 》主 美 离 职 ！ 投身独立种田 游 戏开发_3DM单机</a></li>
<li><a href="https://www.youxituoluo.com/534818.html">youxituoluo.com/534818.html</a></li>

</ul>
</details>

**Tags**: `#gaming industry`, `#miHoYo`, `#game development`, `#artist departure`, `#indie game`

---

<a id="item-tech-news-18"></a>
### [NetEase Q2 2026: Game Revenue 25B RMB, New Titles in Testing](https://www.youxituoluo.com/534816.html) ⭐️ 4.0/10

NetEase reported Q2 2026 net revenue of RMB 30.1 billion \($4.4 billion\), up 7.9% year-over-year, with net profit attributable to shareholders at RMB 7 billion \($1 billion\). Game and related value-added services revenue reached RMB 25 billion \($3.7 billion\), a 9.7% increase, driven by classic IPs like Fantasy Westward Journey and new titles such as Where Winds Meet and Marvel Rivals. The company highlighted stable operating efficiency, with total operating expenses of RMB 9.1 billion, up only 1.5% year-over-year, as growth relied on content innovation rather than heavy user acquisition. Several upcoming titles entered intensive testing, including Guiying Cangfeng \(started first test on August 7\), Wuhai Zhixia \(started testing on August 17\), and Shanhai Qilv \(started first test on July 24\). NetEase also announced that Infinity Nikki will appear at Gamescom Opening Night Live on August 26, 2026, with new project updates.

rss · 游戏陀螺 · Aug 21, 11:11

**「Background」** NetEase is a major Chinese internet technology company with a significant gaming business, known for long-running titles like Fantasy Westward Journey and Justice Online. The company has been expanding its portfolio with new games and international releases, such as Marvel Rivals and Where Winds Meet, to diversify revenue streams. This quarterly earnings report provides insight into the company&\#x27;s financial health and strategic direction.

**「Impact」** For gamers and investors, NetEase&\#x27;s strong Q2 performance and robust pipeline signal continued growth and innovation in the gaming sector, with new titles like Infinity Nikki and Guiying Cangfeng potentially expanding the company&\#x27;s market reach. The company&\#x27;s focus on content-driven growth may set a precedent for sustainable development in the industry.

**Tags**: `#NetEase`, `#earnings`, `#gaming`, `#financial report`, `#business`

---

<a id="item-tech-news-19"></a>
### [Take-Two subpoenas Microsoft and Discord to unmask GTA 6 leaker](https://www.eurogamer.net/take-two-legal-action-gta-6-leeks-cyberleek) ⭐️ 4.0/10

Take-Two Interactive, parent company of Rockstar Games, has filed multiple subpoenas in a federal district court to compel Microsoft and Discord to provide records that could identify the person or persons who leaked Grand Theft Auto VI gameplay videos online. The subpoenas seek data from OneDrive, Xbox accounts, and Discord users that may be sufficient to identify the individuals involved. This legal action follows a week of takedown efforts by Take-Two as the leakers continued to distribute more clips across the internet. The move marks an escalation in the company&\#x27;s response to the leak, which involved a playable build of the game.

rss · Eurogamer · Aug 21, 15:55

**「Background」** Grand Theft Auto VI is one of the most anticipated video games, and its development has been closely guarded by Rockstar Games. Leaks of gameplay footage are rare and often trigger aggressive legal responses from publishers to protect intellectual property and maintain marketing control. Subpoenas are legal orders that require companies to produce evidence, and in this case, they are used to trace the source of the leaked content through digital platforms.

**「Impact」** If successful, the subpoenas could lead to the identification and potential legal action against the leaker, setting a precedent for how game companies pursue anonymous online leakers. The outcome may also affect how platforms like Discord and Microsoft handle user data requests in future leak investigations.

**Tags**: `#gaming`, `#legal`, `#GTA 6`, `#Take-Two`, `#leak`

---

<a id="item-tech-news-20"></a>
### [Plague Tale Resonance Leaks Online Ahead of Launch](https://www.eurogamer.net/plague-tale-resonance-leaked-pc) ⭐️ 4.0/10

A new game in the Plague Tale series, titled Resonance: A Plague Tale Legacy, appears to have been cracked and shared online a week before its official release. The leak means that spoilers may start circulating on the internet, prompting a warning for fans to be cautious about what they watch and read. The game is reportedly available on PC, and the leak could impact the developer&\#x27;s launch plans and sales. Eurogamer reported the news, highlighting the risk of spoilers for the upcoming title.

rss · Eurogamer · Aug 21, 13:01

**「Background」** The Plague Tale series, developed by Asobo Studio and published by Focus Entertainment, is known for its narrative-driven gameplay set in medieval France during the Black Death. The series has gained a dedicated following, and a new installment would be highly anticipated. Game leaks, especially those occurring close to launch, are a common issue in the industry, often leading to spoilers and potential financial impact.

**「Impact」** Fans of the Plague Tale series who wish to avoid spoilers should be cautious online in the week leading up to the game&\#x27;s release, as leaked content may appear on social media and forums. The leak could also affect the game&\#x27;s commercial performance, though the extent is uncertain.

**Tags**: `#gaming`, `#leak`, `#industry news`

---

<a id="item-tech-news-21"></a>
### [Cyberpunk: Edgerunners 2 Premieres October 20](https://www.rockpapershotgun.com/the-lines-between-redemption-and-revenge-will-blur-promises-cyberpunk-edgerunners-2s-latest-trailer-as-the-series-locks-in-a-late-october-release) ⭐️ 4.0/10

Cyberpunk: Edgerunners 2, the second anime series from CD Projekt Red and Netflix set in the Cyberpunk 2077 universe, will premiere on October 20th. A new trailer teases a story centered on themes of revenge and redemption, following four newly revealed Night City residents. The series continues the collaboration between the game developer and the streaming platform, expanding the cyberpunk narrative beyond the original game. The exact release time and episode count have not been disclosed in the announcement.

rss · Rock Paper Shotgun · Aug 21, 12:00

**「Background」** Cyberpunk: Edgerunners is an anime series produced by Studio Trigger and released by Netflix in 2022, set in the same universe as the video game Cyberpunk 2077. It follows a street kid trying to survive in the dangerous, tech-enhanced metropolis of Night City. The success of the first series led to the commissioning of a second season, which continues to explore the lives of new characters in this dystopian setting.

**「Impact」** Fans of the Cyberpunk franchise and anime enthusiasts can expect a new installment that deepens the lore of Night City, potentially influencing future game expansions or other media. The release date provides a concrete timeline for viewers to anticipate the continuation of the series.

**Tags**: `#Cyberpunk`, `#anime`, `#Netflix`, `#release date`, `#trailer`

---

<a id="item-tech-news-22"></a>
### [Among Shadows Preview: Dark Fantasy RPG with Social Deduction](https://www.rockpapershotgun.com/among-shadows-is-a-nightreign-style-dark-fantasy-rpg-with-a-touch-of-among-us-that-makes-me-think-wistfully-of-dark-souls-at-its-most-treacherous) ⭐️ 4.0/10

Among Shadows is an upcoming dark fantasy action-RPG that blends Elden Ring: Nightreign-style combat and exploration with Among Us-like social deduction. Players join the Order of the Secret Fire to investigate a blighted region, track corruption sources, and loot gear while leveling up. The preview notes that the genre mix could be less than the sum of its parts, but the author is cautiously enthusiastic about themes of disease and betrayal. The game&\#x27;s exact release date and platforms have not been announced.

rss · Rock Paper Shotgun · Aug 21, 11:42

**「Background」** Elden Ring: Nightreign is an upcoming cooperative spin-off of Elden Ring that emphasizes fast-paced, session-based combat and exploration. Among Us is a multiplayer social deduction game where players identify impostors among a crew. Among Shadows combines these mechanics, placing players in a cooperative fantasy setting where some may be secretly working against the group.

**「Impact」** For fans of dark fantasy RPGs and social deduction games, Among Shadows could offer a novel hybrid experience, though its success depends on balancing cooperative and adversarial gameplay. The game is still in preview stages, so its final quality and reception remain uncertain.

**Tags**: `#gaming`, `#preview`, `#dark fantasy`, `#social deduction`, `#RPG`

---

