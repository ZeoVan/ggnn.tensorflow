int main()                            //?????
{
	int n=0;
	int a[81]={0};                    //???????81???
	int *p=&a[0];                     //???????????????
	char s[42];
	cin>>n;
	cin>>s;                           //?????????????
	cout<<s;
	p=p+strlen(s);                    //?????????strlen?s????
	for(int i=0;i<n-1;i++)            
	{
		cin>>s;        
		if(p+strlen(s)<&a[80])         //??????????????????strlen?s????????????????????????????????????strlen(s)+1???
			cout<<" "<<s,p=p+strlen(s)+1;
		else                             //??????????strlen?s?????????????????????????????????&a?0?+strlen?s?
		{
			cout<<endl;
			cout<<s;
			p=&a[0]+strlen(s);		
		}
	}
	return 0;
}