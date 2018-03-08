# 图片路径有一些小问题，原来是/img/img.png，在hexo中是/img/img.png
# 用sed进行替换, -i表示修改原文件，g表示将遇到的所有匹配的都替换（不然只替换每行第一个）

fun(){
	for file in $1/*
	do
	    if test -f $file
	    then
	        echo $file 是文件
		sed -i 's/public\/img/img/g' $file
	    fi
	    if test -d $file
	    then
	        echo $file 是目录
		fun $file
	    fi
	done
}

fun .

