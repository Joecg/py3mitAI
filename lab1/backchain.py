from production import AND, OR, NOT, PASS, FAIL, IF, THEN, \
     match, populate, simplify, variables
from zookeeper import ZOOKEEPER_RULES

# This function, which you need to write, takes in a hypothesis
# that can be determined using a set of rules, and outputs a goal
# tree of which statements it would need to test to prove that
# hypothesis. Refer to the problem set (section 2) for more
# detailed specifications and examples.

# Note that this function is supposed to be a general
# backchainer.  You should not hard-code anything that is
# specific to a particular rule set.  The backchainer will be
# tested on things other than ZOOKEEPER_RULES.


def backchain_to_goal_tree(rules, hypothesis):
    unbound = [ (rule.antecedent(),
                 match(rule.consequent()[0], hypothesis))
                for rule in rules if not
                match(rule.consequent()[0], hypothesis)
                is None ]
    bound = OR( hypothesis )
    for (ante, binding) in unbound:
        if type(ante) is AND:
            node_list = [populate(exp, binding)
                         for exp in ante]
            bound.append(AND([backchain_to_goal_tree(rules, node)
                              for node in node_list]))
        elif type(ante) is OR:
            node_list = [populate(exp, binding)
                         for exp in ante]
            bound.append(OR([backchain_to_goal_tree(rules, node)
                             for node in node_list]))
        else:
            node = populate(ante, binding)
            bound.append(backchain_to_goal_tree(rules, node))
    return simplify(bound)


# Here's an example of running the backward chainer - uncomment
# it to see it work:
#print(backchain_to_goal_tree(ZOOKEEPER_RULES, 'opus is a penguin'))
