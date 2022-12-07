from scipy.stats import fisher_exact
import json

def do_go(gene_set, species, way):
    NN = [] # 此文件里的全部uniprot id
    with open('client/static/client/enrichment/goa/goa_' + species + '.json', 'r', encoding='UTF-8') as f:
        go = json.load(f)
    f.close()
    f = open('client/static/client/enrichment/goa/goa_' + species + '.gaf', 'r')
    for l in f:
        sp = l.rstrip().split('\t')
        NN.append(sp[1])
    f.close()
    goid = {}  # ID：name
    gotp = {}  # ID：namespace
    gid = ''
    name = ''
    tp = ''
    f = open('client/static/client/enrichment/go.obo', 'r')
    for l in f:
        l = l.rstrip()  # 删除每行后的空格
        if l == '[Term]':
            if gid != '' and name != '' and tp != '':
                goid[gid] = name
                gotp[gid] = tp
            gid = ''
            name = ''
            tp = ''
        if l.startswith('id: GO:'):
            gid = l.split('id: ')[1]
        if l.startswith('name: '):
            name = l.split('name: ')[1][0].upper() + l.split('name: ')[1][1:]
        if l.startswith('namespace: '):
            tp = l.split('namespace: ')[1]
    f.close()
    MM = {}
    gene = {}
    for sp in gene_set:
        if sp in NN:
            MM[sp] = ''
        gene[sp] = ''
    if len(MM) == 0:
        return -1
    ad = []
    for gg in go:  # go
        mm, nn = [], []
        sss = []
        for gx in MM:
            if gx in go[gg]:
                mm.append(gx)
        go[gg] = set(go[gg])
        m = len(mm)
        M = len(MM)
        n = len(go[gg])
        N = len(NN)
        p = fisher_exact([[m, M - m], [n - m, N - n - M + m]])
        if gg not in goid.keys() or gg not in gotp.keys():
            continue
        elif mm:
            e = float((m / M) / (n / N))
            if way == 'go':
                sss.append(gg)
                sss.append(goid[gg])
                sss.append(gotp[gg])
                #  sss.append(m)
                #  sss.append(M)
                #  sss.append(m / M)
                #  sss.append(n)
                #  sss.append(N)
                #  sss.append(n / N)
                sss.append('{:.2e}'.format(float(e)))
                sss.append('{:.2e}'.format(float(p[1])))
                #      sss.append(mm)
                ad.append(sss)
            elif way == 'bp':
                if gotp[gg] == 'Biological Process':
                    sss.append(gg)
                    sss.append(goid[gg])
                    sss.append(gotp[gg])
                    sss.append('{:.2e}'.format(float(e)))
                    sss.append('{:.2e}'.format(float(p[1])))
                    ad.append(sss)
            elif way == 'mf':
                if gotp[gg] == 'Molecular Function':
                    sss.append(gg)
                    sss.append(goid[gg])
                    sss.append(gotp[gg])
                    sss.append('{:.2e}'.format(float(e)))
                    sss.append('{:.2e}'.format(float(p[1])))
                    ad.append(sss)
            elif way == 'cc':
                if gotp[gg] == 'Cellular Component':
                    sss.append(gg)
                    sss.append(goid[gg])
                    sss.append(gotp[gg])
                    sss.append('{:.2e}'.format(float(e)))
                    sss.append('{:.2e}'.format(float(p[1])))
                    ad.append(sss)

    return ad


def do_kegg(gene_set, species):
    abb_dict = {'yeast': 'sce', 'human': 'hsa', 'arabidopsis': 'ath', 'mouse': 'mmu', 'rat': 'rno', 'fly': 'dme',
                'pig': 'ssc', 'cow': 'bta', 'dog': 'cfa', 'chicken': 'gga', 'worm': 'cel', 'zebrafish': 'dre'}
    abb = abb_dict[species]
    eid = {}
    f = open('client/static/client/enrichment/genes_uniprot.list', 'r')
    for l in f:
        if abb + ':' not in l:
            continue
        sp = l.rstrip().replace('up:', '').split('\t')
        if sp[0] in eid:
            eid[sp[0]] = eid[sp[0]] + [sp[1]]
        else:
            eid[sp[0]] = [sp[1]]
    go = {}
    gog = {}
    f.close()
    f = open('client/static/client/enrichment/genes_pathway.list', 'r')
    for l in f:
        if 'path:' + abb in l:
            sp = l.rstrip().split('\t')
            if sp[0] in eid:
                sp[1] = sp[1].replace('path:' + abb, '')
                if sp[1] in go:
                    go[sp[1]] = go[sp[1]] + eid[sp[0]]
                else:
                    go[sp[1]] = eid[sp[0]]
                for k in eid[sp[0]]:
                    gog[k] = ''
    goid = {}
    gotp = {}
    tp = ''
    f.close()
    f = open('client/static/client/enrichment/pathway.list', 'r')
    for l in f:
        l = l.rstrip()
        if l.startswith('##'):
            tp = l[2:]
        sp = l.split('\t')
        if '#' not in l:
            goid[sp[0]] = sp[1]
            gotp[sp[0]] = tp
    f.close()
    NN = {}
    bgene = {}
    f = open('client/static/client/enrichment/uniprot/uniprot_' + species + '.fasta', 'r')
    for l in f:
        l = l.rstrip()
        if l.startswith('>'):
            id = l.split('|')[1]
            if id in gog:
                NN[id] = ''
            bgene[id] = ''
    MM = {}
    gene = {}
    f.close()
    for sp in gene_set:
        if sp not in bgene:
            bgene[sp] = ''
            if sp in gog:
                NN[sp] = ''
        if sp in gog:
            MM[sp] = ''
        gene[sp] = ''
    if len(MM) == 0:
        return -1
    ad = []
    for gg in go:
        mm = []
        nn = []
        sss = []
        mm1 = {}
        for gx in MM:
            if gx in go[gg]:
                mm.append(gx)

        for gx in NN:
            if gx in go[gg]:
                nn.append(gx)
        m = len(mm)
        M = len(MM)
        n = len(nn)
        N = len(NN)

        p = fisher_exact([[m, M - m], [n - m, N - n - M + m]])
        if n == 0:
            continue
        elif mm:
            e = float((m / M) / (n / N))
            sss.append(abb + gg)
            sss.append(goid[gg])
            sss.append(gotp[gg])
            sss.append('{:.2e}'.format(float(e)))
            sss.append('{:.2e}'.format(float(p[1])))
            ad.append(sss)
    return ad


def do_gesa(gene_set, way):
    gene_set = uniprot2gene(gene_set, 'human')
    f = open('client/static/client/enrichment/gsea/' + way + '.gmt', 'r')
    way_list = {}
    URL = {}
    NN = set()
    for l in f:
        sp = l.rstrip().split('\t')
        way_list[sp[0]] = [sp[2]]
        URL[sp[0]] = [sp[1]]
        NN.add(sp[2])
        for i in range(3, len(sp)):
            way_list[sp[0]] = way_list[sp[0]] + [sp[i]]
            NN.add(sp[i])
    f.close()
    MM = set()
    for l in gene_set:
        if l in NN:
            MM.add(l)
    if len(MM) == 0:
        return -1
    ad = []
    for way in way_list:  # go
        m = 0
        n = 0
        sss = []
        for gx in MM:
            if gx in way_list[way]:
                m += 1
        if m == 0:
            continue

        n = len(way_list[way])

        M = MM.__len__()
        N = NN.__len__()

        p = fisher_exact([[m, M - m], [n - m, N - n - M + m]])
        e = float((m / M) / (n / N))

        sss.append(way)
        sss.append(URL[way])
        sss.append('{:.2e}'.format(float(e)))
        sss.append('{:.2e}'.format(float(p[1])))
        ad.append(sss)
    return ad


def do_do(gene_set):

    gene_set = uniprot2gene(gene_set, 'human')

    file = open('client/static/client/enrichment/do_allgenes.txt', 'r', encoding='utf-8')
    DO = {}
    NN = set()
    for i in file:
        curLine = i.strip().split('\t')
        genes = curLine[8].strip().split('/')
        DO[curLine[0].split('DOID:')[1]] = genes
        for g in genes:
            NN.add(g)
    file.close()
    Name = {}  # ID：name
    gid = ''
    name = ''

    f = open('client/static/client/enrichment/HumanDO.obo', 'r', encoding='utf-8')
    for l in f:
        l = l.rstrip()  # 删除每行后的空格
        if l == '[Term]':
            if gid != '' and name != '':
                Name[gid] = name
            gid = ''
            name = ''
        if l.startswith('id: DOID:'):
            gid = l.split('id: DOID:')[1]

        if l.startswith('name: '):
            name = l.split('name: ')[1]
    f.close()
    MM = {}
    for sp in gene_set:
        if sp in NN:
            MM[sp] = ''

    if len(MM) == 0:
        return -1

    ad = []
    for dd in DO:
        mm, nn = [], []
        sss = []
        # mm1 = {}
        for gx in MM:
            if gx in DO[dd]:
                mm.append(gx)

        DO[dd] = set(DO[dd])
        m = len(mm)
        M = len(MM)
        n = len(DO[dd])
        N = 5063
        # print('m：{} M：{} n：{} N：{}'.format(m, M, n, N))
        p = fisher_exact([[m, M - m], [n - m, N - n - M + m]])
        if mm:
            e = float((m / M) / (n / N))
            sss.append('DO:'+dd)
            sss.append(Name[dd])
            sss.append('{:.2e}'.format(float(e)))
            sss.append('{:.2e}'.format(float(p[1])))
            #      sss.append(mm)
            ad.append(sss)

    return ad


def gene2uniprot(gene_list, species):
    f = open('client/static/client/enrichment/p2g/' + species + '.fasta', 'r')
    uniprot_list = []
    for l in f:
        s = l.rstrip().split('\t')
        u = s[0]  # uniprot id
        g = s[1]
        for i in gene_list:
            if i == g:
                uniprot_list.append(u)
    return uniprot_list


def uniprot2gene(uniprot_list, species):
    f = open('client/static/client/enrichment/p2g/' + species + '.fasta', 'r')
    gene_list = []
    for l in f:
        s = l.rstrip().split('\t')

        u = s[0]  # uniprot id
        g = s[1]
        for i in uniprot_list:
            if i == u:
                gene_list.append(g)
    return gene_list
