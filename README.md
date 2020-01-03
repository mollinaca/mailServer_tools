# mailServer_tools
for my mailServer

## denied IP list

https://mollinaca.github.io/mailServer_tools/denyip.txt

# Environment & requirements

Amazon Linux release 2 (Karoo)  
python3(3.7.4)  
pip3 - aws, awscli, urllib3  

# what to do
(1) 1時間あたりのメールの sent数/reject数 をSlackへつぶやく

(2) メール、および関連ログから、アタックと思われるIPアドレスを抜き出し、NACLで拒否する

(3) NACLの精査、上限に達している場合は解除して余裕を作る

