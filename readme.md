# architecture patterns with python

https://github.com/cosmicpython

## 할당에 대한 노트

- 제품은 sku(stock keeping unit) 로 식별된다.
- 고객은 주문(Order)을 넣는다. 주문은 주문 참조 번호(order referece)에 의해서 식별되며 한줄 이상의 주문 라인(OrderLine)을 포함한다.
- 각 주문 라인에는 sku 와 수량이 있다.

  - 예시) RED-CHAIR 10 단위
  - 예시) TASTELESS-LAMP 1 단위

- 구매 부서는 재고를 작은 배치(batch) 로 주문한다.
- 재고 배치는 유일한 id(orderid), sku, 수량으로 이루어진다.
- 배치에 주문 라인을 할당해야 한다. 주문 라인을 배치에 할당하면 해당 배치에 속하는 재고를 고객의 주소로 배송한다.
- 어떤 배치의 재고를 주문 라인에 x 단위로 할당하면 가용 재고 수량은 x 만큼 줄어든다.
  - 예시) 20 단위의 SMALL-TABLE 로 이루어진 배치가 있고, 2단위의 SMALL-TABLE 을 요구하는 주문 라인이 있다.
  - 주문 라인을 할당하면 배치에 1 단위의 SMALL-TABLE 이 남아야 한다.
- 배치의 가용 재고 수량이 주문 라인 수량보다 작으면 이 주문 라인을 배치에 할당할 수 없다.
