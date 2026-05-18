#登录接口
curl 'https://aepub.58v5.cn/auth/login/v2' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'busid: 100002' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'uuid=CroD5GnfCLg2aI1hAwRlAg==; AWX_RISK_ID=4250368ba7c59550e1e7d477a6da4ca7b912892b_260415; __AWX_TEMP_F_D__=09c00484dc725d5c9829507d9a6a57a7; _ga=GA1.1.244061760.1778586741; accept_cookie=%7B%22version%22%3A2%2C%22functional%22%3A%5B%22last_country%22%2C%22last_language%22%2C%22last_location_name%22%2C%22last_city_code%22%2C%22has_viewed_home%22%2C%22has_selected_language%22%2C%22promoBannerShow%22%2C%22last_property_cate%22%5D%2C%22essential%22%3A%5B%22tk*%22%2C%22uid*%22%2C%22JSESSIONID%22%2C%22accept_cookie%22%2C%22acw_tc%22%2C%22cdn_sec_tc%22%2C%22sec_tc%22%2C%22uuid%22%5D%2C%22analytical%22%3A%5B%22_ga%22%2C%22_ga_Z05SHT8Y7Y%22%5D%2C%22advertising%22%3A%5B%22__gads%22%5D%2C%22all%22%3A%5B%22tk*%22%2C%22uid*%22%2C%22JSESSIONID%22%2C%22accept_cookie%22%2C%22acw_tc%22%2C%22cdn_sec_tc%22%2C%22sec_tc%22%2C%22last_country%22%2C%22last_language%22%2C%22last_location_name%22%2C%22last_city_code%22%2C%22has_viewed_home%22%2C%22has_selected_language%22%2C%22promoBannerShow%22%2C%22last_property_cate%22%2C%22uuid%22%2C%22_ga%22%2C%22_ga_Z05SHT8Y7Y%22%2C%22__gads%22%5D%2C%22isChecked%22%3A1%7D; last_language=AE:en; last_city_code=AE:abu-dhabi; JSESSIONID=4kxOk_xWBI8NOcSnMuDU-PNkmg8s6hKjocnkBOly; last_country=ae; last_location_name=Abu%20Dhabi; _ga_3GVZ60N1SQ=GS2.1.s1778586741$o1$g1$t1778590199$j60$l0$h0; _ga_Z05SHT8Y7Y=GS2.1.s1778586741$o1$g1$t1778590212$j47$l0$h1725924746' \
  -H 'country: AE' \
  -H 'language: en' \
  -H 'origin: https://ae.58v5.cn' \
  -H 'platform: -1' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://ae.58v5.cn/' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'uuid: smhzh3khxo1776224440635' \
  --data-raw '{"accountType":"email","account":"wangyongli@58.com","password":"kk52Bib31nyV5jr4OT5+9yuegAryZCmU9RliD7oUhYJYMoYSgn28Cq3PtOCwJAUGPwtkErq6Ar4XO1ossU+AvZ+gPgPv/czDXns/oe6KGdaBpYA/smipVBby5Do5kzsWivqS+gL46pWUfSR1yyoildmOEd9cH8Xd8yTxcqIfhg3S5+ow0aLPQWLoUqfIDHNiyirZTNqPtuRYLv1OjK/IMvk5X/OqEmU4JtWm1pZoLJ4979+dbbVgCijLLdxmP2Nn93b7fRAybsw6h4lMZn7acXUnT0JpTv0wA9qAtbQSyL17tMH/Leuk/WQa8AYhSvWkb3SUZwCYnP0uweWoYyjOtQ=="}'


#发帖接口
curl 'https://aepub.58v5.cn/easypost/api/posts/publish' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'busid: 100002' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -b 'uuid=CroD5GnfCLg2aI1hAwRlAg==; AWX_RISK_ID=4250368ba7c59550e1e7d477a6da4ca7b912892b_260415; __AWX_TEMP_F_D__=09c00484dc725d5c9829507d9a6a57a7; _ga=GA1.1.244061760.1778586741; accept_cookie=%7B%22version%22%3A2%2C%22functional%22%3A%5B%22last_country%22%2C%22last_language%22%2C%22last_location_name%22%2C%22last_city_code%22%2C%22has_viewed_home%22%2C%22has_selected_language%22%2C%22promoBannerShow%22%2C%22last_property_cate%22%5D%2C%22essential%22%3A%5B%22tk*%22%2C%22uid*%22%2C%22JSESSIONID%22%2C%22accept_cookie%22%2C%22acw_tc%22%2C%22cdn_sec_tc%22%2C%22sec_tc%22%2C%22uuid%22%5D%2C%22analytical%22%3A%5B%22_ga%22%2C%22_ga_Z05SHT8Y7Y%22%5D%2C%22advertising%22%3A%5B%22__gads%22%5D%2C%22all%22%3A%5B%22tk*%22%2C%22uid*%22%2C%22JSESSIONID%22%2C%22accept_cookie%22%2C%22acw_tc%22%2C%22cdn_sec_tc%22%2C%22sec_tc%22%2C%22last_country%22%2C%22last_language%22%2C%22last_location_name%22%2C%22last_city_code%22%2C%22has_viewed_home%22%2C%22has_selected_language%22%2C%22promoBannerShow%22%2C%22last_property_cate%22%2C%22uuid%22%2C%22_ga%22%2C%22_ga_Z05SHT8Y7Y%22%2C%22__gads%22%5D%2C%22isChecked%22%3A1%7D; last_language=AE:en; last_city_code=AE:abu-dhabi; uid100002=796133836057336352; tk100002=bHfGyFQYIXTeYPKMaBbqd0F9EWWYc6u622RjcSNpuy6kvj3ikZLmL8VVlojc2T63duuOm4exEOMMpHXVEU_kUcfeiLDMBhehyivd1z9PMQplIkiBObWiEv_CcnMqHumIOjZRG449MfJkfT39G6ZqXwZMMj4izkZXuNEc8Xe9WrCGIBAuFiBSVS618qs3oCu-UXdZu1j7u2dn2RUUjDKSQCwKS3o6TM8rifLsYEVZWCs; last_country=AE; last_location_name=United%20Arab%20Emirates; _ga_3GVZ60N1SQ=GS2.1.s1778586741$o1$g1$t1778588559$j60$l0$h0; _ga_Z05SHT8Y7Y=GS2.1.s1778586741$o1$g1$t1778588559$j52$l0$h1725924746; JSESSIONID=A206056C8364A200F2FE9B3C842604AD' \
  -H 'country: AE' \
  -H 'language: en' \
  -H 'origin: https://aepub.58v5.cn' \
  -H 'platform: -1' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://aepub.58v5.cn/biz/en/publish/classified?traceId=1778588565526' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  --data-raw '{"country":"AE","source":2,"title":"iphone-14-pro-max-seller-pays-postage-20260402171737 aitest","content":"iphone-14-pro-max-seller-pays-postage-20260402171737 aitest","cateId":10032,"addr":{"detail":"Abu Dhabi","standard":{"country":"United Arab Emirates","countryCode":"AE","administrative_area_level_1":"Abu Dhabi","administrative_area_level_2":"Abu Dhabi Region","administrative_area_level_3":"","administrative_area_level_4":"","administrative_area_level_5":"","administrative_area_level_6":"","administrative_area_level_7":"","locality":"Abu Dhabi","postal_town":"","sublocality_level_1":"","sublocality_level_2":"","sublocality_level_3":"","sublocality_level_4":"","sublocality_level_5":"","addressComponents":[{"longText":"Abu Dhabi","shortText":"Abu Dhabi","types":["locality","political"]},{"longText":"Abu Dhabi Region","shortText":"Abu Dhabi Region","types":["administrative_area_level_2","political"]},{"longText":"Abu Dhabi","shortText":"Abu Dhabi","types":["administrative_area_level_1","political"]},{"longText":"United Arab Emirates","shortText":"AE","types":["country","political"]}]},"fullAddress":"","coordinate":[{"lonti":54.3773438,"lati":24.453884,"axes":"WGS-84"}]},"pics":["https://easypost.58v5.cn/iphone11_1778588582065.jpg?ow=450&oh=450"],"videos":[],"price":{"amount":"888","currency":{"id":3,"name":"UAE Dirham","value":"AED ","code":"AED","prevId":0,"childNum":0,"attrId":0}},"isBiz":0,"isDraft":2,"publishType":2,"secondhandAttrs":{"customizedBrand":"","deliverType":1,"deliverPayer":2,"transactionType":1,"pickup":0},"attrs":[{"id":"30","value":"4"},{"id":"163","value":""},{"id":"164","value":""},{"id":"804","value":""}]}'