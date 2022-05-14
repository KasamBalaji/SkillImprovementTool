  # k=500
    # userskill = UserSkill.query.filter_by(user_id=session["user_id"]).first()
    # errors = []
    # queries = {}
    # for skill in skills:
    #     if userskill.skill_values.get(skill) is None:
    #         errors.append(skill)
    #         continue
    #     skillvalue = userskill.skill_values[skill]
    #     queries[skill] = f"CAST(skill_values->>'{skill}' AS INTEGER) BETWEEN {skillvalue-k} AND {skillvalue+k}"
    
    # if len(errors)>0:
    #     print(errors)
    
    # task_ids = []
    # for length in range(1,len(skills)+1):
        
    #     st = "SELECT task_id FROM task_skills WHERE "
    #     ed = f" length ={length}"
    #     combos = list(itertools.combinations(skills,length))
    #     for combo in combos:
    #         sql = st
    #         for skill in combo:
    #             sql += queries[skill]+ " AND "
    #         sql +=ed
    #         res = db.engine.execute(sql).fetchall()
    #         res =list(itertools.chain(*res))
    #         print(res)
    #         task_ids.extend(res)
    # print(task_ids)

    # for skill in skills:
    #     obs_sql = sqls["OB_PF"].format(skill=skill,user_id=1)
    #     ob =db.engine.execute(obs_sql).fetchone()
    #     if ob[2] is not None:
    #         exp_sql = sqls["EXP_PF"].format(skill=skill,user_id=1,lower=ob[2]-100,upper=ob[2]+100)
    #         exp = db.engine.execute(exp_sql).fetchone()
    #         d = math.sqrt((exp[0]-ob[0])**2 + (exp[1]-ob[1])**2)
    #         s = math.erf(d)
    #         print(ob)
    #         print(exp)
    #         print(s)
    pfs = {'HTML':0.5,'CSS':0.7,'JS':0.8}

    task_ids= [1,2,3,4,5,6]
    task_values ={}
    for task_id in task_ids:
            query = f"SELECT skill_values FROM task_skills where task_id={task_id}"
            values =db.engine.execute(query).fetchone()[0]
            task_values[task_id]=values
    userskill = UserSkill.query.filter_by(user_id=session["user_id"]).first() 
    # print(userskill.skill_values)
    skillgaps ={}
    # print(task_values)
    for task in task_values.values():
        # print(task)
        for skill in task:
            if skillgaps.get(skill) is None:
                skillgaps[skill]=[]
            skillgaps[skill].append(task[skill] - userskill.skill_values[skill])

    means ={}
    sds ={}
    for skill in skillgaps:
        mean = sum(skillgaps[skill]) / len(skillgaps[skill])
        variance = sum([((x - mean) ** 2) for x in skillgaps[skill]]) / len(skillgaps[skill])
        sd = variance ** 0.5
        means[skill]=mean
        sds[skill]=sd
    learning_potentials = {}
    for task_id in task_values:
        lp =0
        for skill in task_values[task_id]:
            z = (task_values[task_id][skill] - means[skill])/sds[skill]
            lp +=skewnorm.pdf(z,pfs[skill])
        learning_potentials[task_id]=lp
    
    sorted_taskids =dict(sorted(learning_potentials.items(),key=lambda item: item[1]))
    sorted_taskids = OrderedDict(reversed(list(sorted_taskids.items())))
    res = list(sorted_taskids.keys())
    res = res[:min(10,len(res))]
    print(res)

    return 'Hello'+str(res)