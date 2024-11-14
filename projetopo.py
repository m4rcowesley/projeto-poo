from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

# Configuração do banco de dados e sessão
engine = create_engine('sqlite:///cardapio.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Definição das classes Produto, Cliente, PedidoProduto e Pedido
class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<Produto(id={self.id}, nome={self.nome}, preco={self.preco}, estoque={self.estoque})>'

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f'<Cliente(id={self.id}, nome={self.nome}, email={self.email})>'

class PedidoProduto(Base):
    __tablename__ = 'pedido_produto'
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), primary_key=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'), primary_key=True)
    quantidade = Column(Integer, nullable=False)

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    total = Column(Float, nullable=False)

    cliente = relationship('Cliente', backref='pedidos')
    produtos = relationship('Produto', secondary='pedido_produto', backref='pedidos')

    def __repr__(self):
        return f'<Pedido(id={self.id}, cliente_id={self.cliente_id}, total={self.total})>'

# Criação das tabelas no banco de dados
Base.metadata.create_all(engine)

# Funções adicionais

# Consulta de produtos
def consultar_produtos():
    produtos = session.query(Produto).all()
    for produto in produtos:
        print(produto)

# Consulta de clientes
def consultar_clientes():
    clientes = session.query(Cliente).all()
    for cliente in clientes:
        print(cliente)

# Consulta de pedidos
def consultar_pedidos():
    pedidos = session.query(Pedido).all()
    for pedido in pedidos:
        print(pedido)

# Atualização de estoque de um produto
def atualizar_estoque(produto_id, nova_quantidade):
    produto = session.query(Produto).filter_by(id=produto_id).first()
    if produto:
        produto.estoque = nova_quantidade
        session.commit()
        print(f"Estoque do produto '{produto.nome}' atualizado para {nova_quantidade}.")
    else:
        print(f"Produto com ID {produto_id} não encontrado.")

# Cancelamento de produto
def cancelar_produto(produto_id):
    produto = session.query(Produto).filter_by(id=produto_id).first()
    if produto:
        session.delete(produto)
        session.commit()
        print(f"Produto '{produto.nome}' removido com sucesso.")
    else:
        print(f"Produto com ID {produto_id} não encontrado.")

# Cancelamento de cliente
def cancelar_cliente(cliente_id):
    cliente = session.query(Cliente).filter_by(id=cliente_id).first()
    if cliente:
        session.delete(cliente)
        session.commit()
        print(f"Cliente '{cliente.nome}' removido com sucesso.")
    else:
        print(f"Cliente com ID {cliente_id} não encontrado.")

# Histórico de pedidos de um cliente
def historico_pedidos_cliente(cliente_id):
    pedidos = session.query(Pedido).filter_by(cliente_id=cliente_id).all()
    if pedidos:
        print(f"Pedidos do cliente com ID {cliente_id}:")
        for pedido in pedidos:
            print(pedido)
    else:
        print(f"Cliente com ID {cliente_id} não possui pedidos.")

# Funções principais
def adicionar_produto(nome, preco, estoque):
    produto_existente = session.query(Produto).filter_by(nome=nome).first()
    if not produto_existente:
        produto = Produto(nome=nome, preco=preco, estoque=estoque)
        session.add(produto)
        session.commit()
        print(f"Produto '{nome}' adicionado com sucesso!")
    else:
        print(f"Produto '{nome}' já existe na base de dados.")

def adicionar_cliente(nome, email):
    cliente = session.query(Cliente).filter_by(email=email).first()
    if not cliente:
        cliente = Cliente(nome=nome, email=email)
        session.add(cliente)
        session.commit()
        print(f"Cliente '{nome}' adicionado com sucesso!")
    else:
        print(f"Cliente '{email}' já existe na base de dados.")

def adicionar_pedido(cliente_id, produtos_quantidades):
    cliente = session.query(Cliente).filter_by(id=cliente_id).first()
    if not cliente:
        print(f"Cliente com ID {cliente_id} não encontrado.")
        return

    total = 0
    for produto_id, quantidade in produtos_quantidades.items():
        produto = session.query(Produto).filter_by(id=produto_id).first()
        if produto:
            if produto.estoque < quantidade:
                print(f"Produto '{produto.nome}' não tem estoque suficiente.")
                return
            total += produto.preco * quantidade
            produto.estoque -= quantidade
        else:
            print(f"Produto com ID {produto_id} não encontrado.")
            return

    pedido = Pedido(cliente_id=cliente_id, total=total)
    session.add(pedido)
    session.commit()

    for produto_id, quantidade in produtos_quantidades.items():
        pedido_produto = PedidoProduto(pedido_id=pedido.id, produto_id=produto_id, quantidade=quantidade)
        session.add(pedido_produto)

    session.commit()
    print(f"Pedido adicionado com sucesso! Total: {total}")

# Função principal com novas opções
def main():
    while True:
        print('\nEscolha uma opção:')
        print('1. Adicionar Produto')
        print('2. Adicionar Cliente')
        print('3. Adicionar Pedido')
        print('4. Consultar Produtos')
        print('5. Consultar Clientes')
        print('6. Consultar Pedidos')
        print('7. Atualizar Estoque de Produto')
        print('8. Cancelar Produto')
        print('9. Cancelar Cliente')
        print('10. Histórico de Pedidos de um Cliente')
        print('11. Sair')

        try:
            opcao = input('Opção: ')
            if opcao == '1':
                nome = input('Nome do Produto: ')
                preco = float(input('Preço do Produto: '))
                estoque = int(input('Quantidade em Estoque: '))
                adicionar_produto(nome, preco, estoque)
            elif opcao == '2':
                nome = input('Nome do Cliente: ')
                email = input('Email do Cliente: ')
                adicionar_cliente(nome, email)
            elif opcao == '3':
                cliente_id = int(input('ID do Cliente: '))
                produtos_quantidades = {}
                while True:
                    produto_id = int(input('ID do Produto: '))
                    quantidade = int(input('Quantidade do Produto: '))
                    produtos_quantidades[produto_id] = quantidade
                    mais_produtos = input('Deseja adicionar outro produto? (s/n): ').lower()
                    if mais_produtos != 's':
                        break
                adicionar_pedido(cliente_id, produtos_quantidades)
            elif opcao == '4':
                consultar_produtos()
            elif opcao == '5':
                consultar_clientes()
            elif opcao == '6':
                consultar_pedidos()
            elif opcao == '7':
                produto_id = int(input('ID do Produto: '))
                nova_quantidade = int(input('Nova Quantidade: '))
                atualizar_estoque(produto_id, nova_quantidade)
            elif opcao == '8':
                produto_id = int(input('ID do Produto: '))
                cancelar_produto(produto_id)
            elif opcao == '9':
                cliente_id = int(input('ID do Cliente: '))
                cancelar_cliente(cliente_id)
            elif opcao == '10':
                cliente_id = int(input('ID do Cliente: '))
                historico_pedidos_cliente(cliente_id)
            elif opcao == '11':
                print("Saindo...")
                break
            else:
                print('Opção inválida. Tente novamente.')
        except Exception as e:
            print(f"Ocorreu um erro: {e}. Tente novamente.")

if __name__ == "__main__":
    main()
