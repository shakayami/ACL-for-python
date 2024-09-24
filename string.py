class string:
    def sa_is(s,upper):
        n=len(s)
        if n==0:
            return []
        if n==1:
            return [0]
        if n==2:
            if (s[0]<s[1]):
                return [0,1]
            else:
                return [1,0]
        sa=[0]*n
        ls=[0]*n
        for i in range(n-2,-1,-1):
            ls[i]=ls[i+1] if (s[i]==s[i+1]) else (s[i]<s[i+1])
        sum_l=[0]*(upper+1)
        sum_s=[0]*(upper+1)
        for i in range(n):
            if not(ls[i]):
                sum_s[s[i]]+=1
            else:
                sum_l[s[i]+1]+=1
        for i in range(upper+1):
            sum_s[i]+=sum_l[i]
            if i<upper:
                sum_l[i+1]+=sum_s[i]
        def induce(lms):
            for i in range(n):
                sa[i]=-1
            buf=sum_s[:]
            for d in lms:
                if d==n:
                    continue
                sa[buf[s[d]]]=d
                buf[s[d]]+=1
            buf=sum_l[:]
            sa[buf[s[n-1]]]=n-1
            buf[s[n-1]]+=1
            for i in range(n):
                v=sa[i]
                if v>=1 and not(ls[v-1]):
                    sa[buf[s[v-1]]]=v-1
                    buf[s[v-1]]+=1
            buf=sum_l[:]
            for i in range(n-1,-1,-1):
                v=sa[i]
                if v>=1 and ls[v-1]:
                    buf[s[v-1]+1]-=1
                    sa[buf[s[v-1]+1]]=v-1
        lms_map=[-1]*(n+1)
        m=0
        for i in range(1,n):
            if not(ls[i-1]) and ls[i]:
                lms_map[i]=m
                m+=1
        lms=[]
        for i in range(1,n):
            if not(ls[i-1]) and ls[i]:
                lms.append(i)
        induce(lms)
        if m:
            sorted_lms=[]
            for v in sa:
                if lms_map[v]!=-1:
                    sorted_lms.append(v)
            rec_s=[0]*m
            rec_upper=0
            rec_s[lms_map[sorted_lms[0]]]=0
            for i in range(1,m):
                l=sorted_lms[i-1]
                r=sorted_lms[i]
                end_l=lms[lms_map[l]+1] if (lms_map[l]+1<m) else n
                end_r=lms[lms_map[r]+1] if (lms_map[r]+1<m) else n
                same=True
                if end_l-l!=end_r-r:
                    same=False
                else:
                    while(l<end_l):
                        if s[l]!=s[r]:
                            break
                        l+=1
                        r+=1
                    if (l==n) or (s[l]!=s[r]):
                        same=False
                if not(same):
                    rec_upper+=1
                rec_s[lms_map[sorted_lms[i]]]=rec_upper
            rec_sa=string.sa_is(rec_s,rec_upper)
            for i in range(m):
                sorted_lms[i]=lms[rec_sa[i]]
            induce(sorted_lms)
        return sa
    def suffix_array_upper(s,upper):
        assert 0<=upper
        for d in s:
            assert 0<=d and d<=upper
        return string.sa_is(s,upper)
    def suffix_array(s):
        n=len(s)
        if type(s)==str:
            s2=[ord(i) for i in s]
            return string.sa_is(s2,255)
        else:
            idx=list(range(n))
            idx.sort(key=lambda x:s[x])
            s2=[0]*n
            now=0
            for i in range(n):
                if (i and s[idx[i-1]]!=s[idx[i]]):
                    now+=1
                s2[idx[i]]=now
            return string.sa_is(s2,now)
    def lcp_array(s,sa):
        n=len(s)
        assert n>=1
        rnk=[0]*n
        for i in range(n):
            rnk[sa[i]]=i
        lcp=[0]*(n-1)
        h=0
        for i in range(n):
            if h>0:
                h-=1
            if rnk[i]==0:
                continue
            j=sa[rnk[i]-1]
            while(j+h<n and i+h<n):
                if s[j+h]!=s[i+h]:
                    break
                h+=1
            lcp[rnk[i]-1]=h
        return lcp
    def z_algorithm(s):
        n=len(s)
        if n==0:
            return []
        z=[0]*n
        i=1;j=0
        while(i<n):
            z[i]=0 if (j+z[j]<=i) else min(j+z[j]-i,z[i-j])
            while((i+z[i]<n) and (s[z[i]]==s[i+z[i]])):
                z[i]+=1
            if (j+z[j]<i+z[i]):
                j=i
            i+=1
        z[0]=n
        return z
