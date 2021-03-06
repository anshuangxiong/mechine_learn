import hashlib
import json
from time import time
from textwrap import dedent
from uuid import uuid4
from flask import Flask,jsonify,request

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self,proof,previous_hash=None):
        # adds a new transaction to the list of transactions
        """
        生成新块
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash:(Optional)<str>Hash of previous Block
        :return:<dict> New Block
        """
        block={
            'index':len(self.chain)+1,
            'timestamp':time(),
            'transactions':self.current_transactions,
            'proof':proof,
            'previous_hash':previous_hash or self.hash(self.chain[-1])
        }
        # reset the current list of transactions
        self.current_transactions=[]
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        """
        生成块的SHA-256 hash值
        :param block:<dict> Block
        :return:<str>
        """
        # we must make sure that the Dictionary is Ordered,or we'll have inconsistent hashes
        block_string=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # reutrn the last block in the chain
        return self.chain[-1]

    def new_transaction(self,sender,recipient,amount):
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender:<str> Address of the Sender
        :param recipient:<str> Address of the Recipient
        :param amount:<int> Amount
        :return:<int> The index of the block that will hold this transaction
        """
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
        })
        return self.last_block['index']+1

    """
    工作量证明算法pow
    PoW的目标是找出一个符合特定条件的数字，这个数字很难计算出来，但容易验证
    """

    """
    实现工作量证明
        让我们来实现一个相似PoW算法，规则是：
            寻找一个数p，使得它与前一个区块的proof拼接成的字符串的Hash值以4个零开头
    """

    def proof_of_work(self,last_proof):
        """
        简单的工作量证明：
        -查找一个p',使得hash(pp')以四个0开头
        -p是上一个块的证明，p'是当前的证明
        :param last_proof: <int>
        :return: <int>
        """
        proof=0
        while self.valid_proof(last_proof,proof) is False:
            proof+=1
        return proof

    @staticmethod
    def valid_proof(last_proof,proof):
        """
        验证证明：是否hash(last_prooof,proof)以4个0开头？
        :param last_proof: <int>Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if current,False if not
        """
        guess=f'{last_proof}{proof}'.encode()
        guess_hash=hashlib.sha256(guess).hexdigest()
        return guess_hash[:4]=="0000"

app=Flask(__name__)

node_inentifier=str(uuid4()).replace('-','')

blockchain=Blockchain()

@app.route('/mine',methods=["GET"])
def mine():
    # we run the proof of work algorithm to get the next proof....
    last_block=blockchain.last_block
    last_proof=last_block['proof']
    proof=blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=node_inentifier,
        amount=1,
    )

    block=blockchain.new_block(proof)
    response={
        'message':'New Block Forged',
        'index':block['index'],
        'transactions':block['transactions'],
        'proof':block['proof'],
        'previous_hash':block['previous_hash'],
    }
    return jsonify(response),200

@app.route('/transactions/new',methods=["POST"])
def new_transaction():
    values=request.get_json()

    required=['sender','recipient','amount']
    if not all(k in values for k in required):
        return "Missing values",400

    index=blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
    response={
        'message':f'Transaction will be added to Block {index}'
    }
    return jsonify(response),201

@app.route('/chain',methods=["GET"])
def full_chain():
    response={
        'chain':blockchain.chain,
        'length':len(blockchain.chain),
    }
    return jsonify(response),200


from hashlib import sha256
if __name__ == "__main__":
    '''
    print('pow')
    x = 5
    y = 0 #y未知
    
    while sha256(f'{x*y}'.encode()).hexdigest()[-1]!="0":
        y+=1
    print(f'The solution is y={y}')
    '''
    app.run(host='localhost',port=5000)