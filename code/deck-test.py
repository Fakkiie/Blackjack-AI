from blackjackFunctions import * 


s = shoe()

for c in s.cards : 
    s.getNext()
    print(c)
    print('\t\t', s.true_count)
    
    print('\t\t', s.running_count)

print(s.decksDelt)
print(s.cardsDelt)