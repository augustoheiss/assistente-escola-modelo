"""
Início — O Manifesto
Landing page do Assistente Escola Modelo.

Apresenta o projeto, os vídeos de pitch/podcast e o manifesto completo.
É a primeira página da navegação — a vitrine do MVP.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from config.settings import NOME_ESCOLA, MODO_OPERACAO

# ── CSS da Landing Page ───────────────────────────────────────────────────────

st.markdown("""
<style>

/* ══════════ HERO ══════════════════════════════════════════════════════════ */
.lp-hero {
    background: linear-gradient(135deg, #0d1b5e 0%, #1e3a8a 45%, #3b5bdb 80%, #5c7cfa 100%);
    border-radius: 20px;
    padding: 3.5rem 2rem 3rem;
    text-align: center;
    box-shadow: 0 12px 50px rgba(59,91,219,0.35);
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.lp-hero::before {
    content:'';
    position:absolute; top:-60%; right:-8%;
    width:400px; height:400px;
    background:rgba(255,255,255,0.04);
    border-radius:50%; pointer-events:none;
}
.lp-hero::after {
    content:'';
    position:absolute; bottom:-50%; left:-5%;
    width:300px; height:300px;
    background:rgba(255,255,255,0.03);
    border-radius:50%; pointer-events:none;
}
.lp-eyebrow {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    color: #c5cae9;
    font-size: 0.73rem;
    font-weight: 700;
    padding: 3px 16px;
    border-radius: 20px;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.lp-title {
    color: #ffffff !important;
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    margin: 0 0 0.7rem !important;
    letter-spacing: -1px;
    line-height: 1.1;
}
.lp-subtitle {
    color: #a5b4fc;
    font-size: 1.08rem;
    line-height: 1.65;
    max-width: 580px;
    margin: 0 auto 1.6rem;
}
.lp-badges {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.2rem;
}
.lp-badge {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.20);
    color: #e0e7ff;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 20px;
}

/* ══════════ SECTION HEADERS ═══════════════════════════════════════════════ */
.lp-section-label {
    text-align: center;
    margin: 0.5rem 0 1.2rem;
}
.lp-section-label h2 {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1a237e;
    margin: 0 0 0.3rem;
}
.lp-section-label p {
    color: #6b7280;
    font-size: 0.93rem;
    margin: 0;
}

/* ══════════ VIDEO CARDS ════════════════════════════════════════════════════ */
.video-card {
    background: #f8f9ff;
    border: 1px solid #dde3ff;
    border-radius: 14px;
    padding: 1.2rem 1.2rem 0.8rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 3px 16px rgba(59,91,219,0.08);
}
.video-card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a237e;
    margin: 0 0 0.25rem;
}
.video-card-desc {
    font-size: 0.85rem;
    color: #6b7280;
    margin: 0 0 0.9rem;
}

/* ══════════ MANIFESTO CONTENT ══════════════════════════════════════════════ */
.manifesto-body h3 {
    color: #1a237e;
    font-size: 1.15rem;
    font-weight: 800;
    margin: 1.8rem 0 0.6rem;
    border-bottom: 2px solid #e0e7ff;
    padding-bottom: 0.35rem;
}
.manifesto-body p {
    color: #374151;
    font-size: 0.94rem;
    line-height: 1.75;
    margin-bottom: 0.9rem;
}

/* ══════════ CTA SECTION ════════════════════════════════════════════════════ */
.lp-cta {
    background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);
    border: 2px solid #c5cae9;
    border-radius: 16px;
    padding: 2.2rem 2rem;
    text-align: center;
    margin-top: 2.5rem;
    box-shadow: 0 4px 20px rgba(59,91,219,0.08);
}
.lp-cta h3 {
    color: #1a237e;
    font-size: 1.45rem;
    font-weight: 800;
    margin: 0 0 0.6rem;
}
.lp-cta p {
    color: #4b5563;
    font-size: 0.95rem;
    max-width: 500px;
    margin: 0 auto 1.2rem;
    line-height: 1.6;
}
.lp-arrow {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    display: block;
}

</style>
""", unsafe_allow_html=True)


# ── Hero Principal ────────────────────────────────────────────────────────────

_modo_badge = "🟡 Modo Simulação" if MODO_OPERACAO == "mock" else "🟢 Motor RAG Ativo"
st.markdown(
    f'<div class="lp-hero">'
    f'<span class="lp-eyebrow">MVP · {NOME_ESCOLA}</span>'
    f'<h1 class="lp-title">Assistente Escola Modelo</h1>'
    f'<p class="lp-subtitle">'
    f'O manifesto pela automação nobre e a ética do Segundo Atual na educação pública.'
    f'</p>'
    f'<div class="lp-badges">'
    f'<span class="lp-badge">⚙️ Escudo RAG</span>'
    f'<span class="lp-badge">🛡️ Supervisão Humana</span>'
    f'<span class="lp-badge">📋 Logs Auditáveis</span>'
    f'<span class="lp-badge">🔍 Zero Caixa-Preta</span>'
    f'<span class="lp-badge">{_modo_badge}</span>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Seção: Vídeo de Apresentação ──────────────────────────────────────────────

st.markdown(
    '<div class="lp-section-label">'
    '<h2>🎬 Conheça o Projeto</h2>'
    '<p>Assista à apresentação completa do MVP e entenda como a Alavanca funciona na prática.</p>'
    '</div>',
    unsafe_allow_html=True,
)

col_v, col_pad = st.columns([3, 1])
with col_v:
    st.markdown('<div class="video-card">', unsafe_allow_html=True)
    st.markdown(
        '<p class="video-card-title">📽️ Apresentação do MVP</p>'
        '<p class="video-card-desc">Do manifesto ao código — como o Escudo RAG e a supervisão humana trabalham juntos.</p>',
        unsafe_allow_html=True,
    )
    st.video("https://www.youtube.com/watch?v=dX5yKonrWP4")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Seção: Podcast ────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    '<div class="lp-section-label">'
    '<h2>🎙️ Podcast: A Religião da Burocracia</h2>'
    '<p>Um aprofundamento filosófico sobre por que a burocracia escolar virou dogma — e como quebrá-la.</p>'
    '</div>',
    unsafe_allow_html=True,
)

col_p, col_pad2 = st.columns([3, 1])
with col_p:
    st.markdown('<div class="video-card">', unsafe_allow_html=True)
    st.markdown(
        '<p class="video-card-title">🎧 Ouça o episódio completo</p>'
        '<p class="video-card-desc">Da lei da alavanca à ética assimétrica de Levinas — a base filosófica do projeto.</p>',
        unsafe_allow_html=True,
    )
    st.video("https://www.youtube.com/watch?v=yC34sSWONd0")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Seção: Manifesto na Íntegra ───────────────────────────────────────────────

st.divider()

with st.expander("📖 Ler o Manifesto na Íntegra  ·  Tempo de leitura: 5 min", expanded=False):
    st.markdown("""
### Assistente Escola Modelo: O Manifesto do Segundo Atual

Este repositório não contém apenas código; ele contém uma filosofia de trabalho, de eficiência e de libertação da burocracia acadêmica. O Assistente Escola Modelo é uma alavanca tecnológica projetada para devolver o tempo e a humanidade aos profissionais da educação e à comunidade.

---

### Capítulo 1: O Princípio da Alavanca e a Ética do Segundo Atual

Temos muitos 'Papéis' hoje que organizam o trabalho das pessoas. Eles visam o momento em que vivemos, seguem princípios e éticas corporativas e nos ajudam a entender a forma 'correta' ou melhor, a forma mais eficiente de sermos produtivos. Ao considerar esses Papéis, vemos diversas possibilidades de como ter o controle eficiente da nossa função.

No entanto, é difícil enxergar a verdadeira eficiência por trás de tanta burocracia. O 'Segundo Atual' tem múltiplas facetas. Quando chegamos ao ambiente escolar, por exemplo, como funcionários, precisamos fazer uma leitura real do que está acontecendo ali, no agora. Para isso, precisamos entender o princípio de funcionamento de tantos 'papéis' criados pelo homem na sua tentativa de reproduzir a lógica do Universo.

Na visão do estudante, esse cenário é ainda mais difícil. Não apenas porque ele é mais forte e aguenta a pressão — isso o Universo (e Deus) já mostra —, mas porque é complexo não ter ainda a experiência com uma função, um cargo ou uma 'burocracia'. Nós tendemos a confiar na nossa família, mas enxergar o funcionamento do tempo como ele realmente é torna-se um desafio imenso para quem está apenas no início da vida. O estudante não tem uma 'função' burocrática para usar como escudo, como arma ou como míssil. Ele está puramente no momento atual, e não deve achar que esse Tempo, ainda sem uma função determinada, não tem valor.

Na Matemática, as proporções são implacáveis. Quando deixamos algo de lado — por exemplo, se eu reduzo o meu esforço em 50% porque alguém me disse algo que eu não gostei —, para recuperar esse 'poder' do qual abrimos mão, nós precisamos de um esforço multiplicativo de 200%. É assim que funcionam as razões: a queda parece pequena, mas o esforço para recuperá-la é enorme. Não é difícil provar isso; basta ver o quanto as pessoas se esgotam tentando correr atrás do prejuízo.

Mas, como todo bom ser pensante, nós nos adaptamos e temos uma ideia: usamos uma alavanca! Com a física a nosso favor, usando uma ferramenta comprida, aquele esforço de 200% cai pela metade. Ou, melhor ainda, usamos uma correia 10 vezes menor conectada a uma maior, gerando uma força 10 vezes superior. Era desse esforço que estávamos precisando, não é verdade? A matemática é uma maravilha e, ao estudá-la, encontramos a Lógica da Vida. Essa Lógica foi representada também por um ser que aceitou ser o modelo supremo na Terra: Jesus Cristo. Mas não é diretamente sobre Ele que este texto trata. Para estudar a estrutura das civilizações e da eficiência, não precisamos ir tão longe: a resposta está mais perto do que você imagina, basta observar as engrenagens de uma bicicleta!

Então, qual é o objetivo desta explicação inicial? Vivemos em um sistema organizado por pessoas e devemos entender que as coisas no Universo não funcionam da forma como costumamos medir, ou como a nossa intuição diz que 'deveriam' funcionar. Para o filósofo Emmanuel Levinas, por exemplo, a ética não é um conjunto de regras recíprocas. Ele afirma que 'a ética de verdade é, por natureza, assimétrica; as obrigações com o outro devem preceder o cálculo'. A ética é uma responsabilidade incondicional pelo próximo, que nasce antes de qualquer escolha racional.

O livro de Mateus 7:12 diz: 'Portanto, todas as coisas que querem que os homens façam a vocês, façam também a eles. De fato, isso é o que a Lei e os Profetas querem dizer'. Como o versículo aponta, nós desejamos a reciprocidade por natureza. Mas não é seguindo essa simetria de 'toma lá, dá cá' que o Universo de fato opera.

A ideia deste texto é apresentar uma 'nova' ferramenta, alinhada à tecnologia disponível hoje, para juntar todas as coisas de valor de uma maneira dinâmica. Precisamos reconhecer que 'o mundo está passando' (1 João 2:17). O vocabulário que tínhamos 10 anos atrás não cabe mais na velocidade da tecnologia atual. Devemos entrar em um Tempo de Ação e Reação, abandonando a busca cega pelo conforto, pela comodidade e pelos julgamentos alheios.

Alguém pode questionar: 'Mas, com a IA, não estamos dando poder na mão de quem não faz nada?'. Essa afirmação tem base na lei Universal? Voltando à Matemática: se percebemos que alguém deixa de fazer 80% do seu dever e faz apenas o mínimo, deveríamos deixar de implementar uma solução revolucionária só porque esse indivíduo fará o mínimo com ainda menos esforço? É assim que devemos agir? E onde fica a lei da ética assimétrica?

A afirmação de que não deveríamos democratizar uma ferramenta porque alguém pode usá-la 'para o mal' ou para a preguiça não tem justificativa. Cada um é responsável por suas próprias ações. Fazer o trabalho do outro não é ajudar; é carregar um peso que não é seu. Nós devemos trabalhar com total transparência em nossos tratos com as outras pessoas, e é exatamente sobre essa transparência técnica e moral que este manifesto vai se aprofundar.

---

### Capítulo 2: A Busca pela Transparência e a Coragem do "Segundo Atual"

Vamos voltar aos jovens. Você já se perguntou por que eles são tão fortes? O jovem tende a agir sem medo; ele sente que 'não tem nada a perder'. A Bíblia nos conta a história de um homem que, despojado de seus privilégios, de sua classe social e de seu conforto, encontrou a coragem para confrontar aqueles que deveriam apoiá-lo:

> *'Meus próprios irmãos têm sido tão traiçoeiros como um rio temporário... Pois isso é o que vocês se tornaram para mim; Vocês veem o terror da minha calamidade e ficam com medo.'* (Jó 6:15, 21)

É inevitável que o próprio 'Papel' que nós trabalhamos para criar venha, algum dia, agir contra nós mesmos. É inevitável que alguém aja de má-fé ou use a nossa própria eficiência como arma contra nós. Mas a nossa saúde individual não pode ter como base o que sofremos na vida; nós queremos manter a mente sã independentemente das tempestades. Por isso, devemos imitar a força dos jovens: agir sem o medo paralisante do que podem fazer contra nós.

Agir no 'Segundo Atual' é operar sem o medo das funções, das burocracias ou dos Papéis. Nós já entramos em um Novo Tempo, onde a velocidade caminha a passos muito rápidos. Hoje, a produção de empresas inteiras pode ser entregue a uma única pessoa armada com a Inteligência Artificial.

O 'terror da calamidade' citado por Jó é, hoje, a queda do sistema atual. Os nossos 'irmãos' — nossos colegas de profissão, gestores e a própria sociedade — veem a burocracia desmoronar diante da verdadeira eficiência e ficam aterrorizados. Como um rio temporário que seca quando você mais precisa de água, eles recuam e se tornam traiçoeiros para defender a própria zona de conforto.

No entanto, esse medo, embora previsível, é irracional e não deve ser cultivado. A traição do sistema não deve, em hipótese alguma, nos impedir de jogar o 'jogo da proporção'. Se a matemática nos mostra que a alavanca funciona, se a física do Universo nos exige Ação e Reação, nós não podemos recuar por medo de como os outros vão reagir. Não fomos feitos para ser reféns do medo alheio ou da falsa segurança de um cargo.

Quem adora o sistema burocrático vai espernear e tentará nos culpar pela chuva. Mas a nossa lamparina já está acesa. A tempestade não afeta a chama quando ela está protegida; nós temos óleo nela exatamente porque paramos de agir visando apenas um cargo ou uma função. O Novo Tempo não pede permissão para chegar; ele simplesmente chega. E nós decidimos encará-lo de frente, operando a máquina com transparência, deixando que os burocratas lutem sozinhos contra a própria obsolescência.

Já que estamos prestes a mergulhar na verdadeira eficiência do nosso trabalho, precisamos entender o que é o discernimento, a consciência e o livre-arbítrio.

A Inteligência Artificial já possui um discernimento funcional. Ela não 'escuta' você falar para transcrever o áudio em linguagem de sinais ou em texto; ela converte os sinais sonoros em matemática pura para 'saber' qual letra você está usando. Ela discerne a melhor forma de responder através de cálculos profundos.

O filósofo John Searle ilustrou isso com o argumento da Sala Chinesa: imagine uma pessoa que não sabe chinês, mas recebe um manual de regras sobre como manusear símbolos chineses. Para quem está de fora, parece que o homem compreende o idioma, mas ele apenas segue as regras. Da mesma forma opera a IA: o seu discernimento e a sua consciência funcional são determinísticos. Eles são determinados pelos fatores, princípios e vieses que nós — os humanos — programamos nela. Se não aplicarmos a transparência correta, a máquina aprenderá a reproduzir nossos preconceitos e erros.

Mas as nossas ações humanas também não são determinísticas? O apóstolo Paulo escreveu:

> *'Não sobreveio a vocês nenhuma tentação a não ser as que são comuns aos homens. Mas Deus é fiel, e ele não deixará que vocês sejam tentados além do que podem suportar; mas, quando vier a tentação, ele também providenciará a saída, para que a possam suportar.'* (1 Coríntios 10:13)

Existem teorias quânticas que afirmam que, se tivéssemos a capacidade de calcular todas as variáveis do Universo, descobriríamos que o homem não tem livre-arbítrio. Chegar a essa conclusão para justificar a inércia é óbvio e inútil. Nós nunca seremos o 'Sabe Tudo'. Podemos estudar as formigas, o pó da terra e o tempo por toda a Eternidade, e as variáveis nunca terão fim.

O fato de sermos influenciados pelo meio não deve nos fazer tomar conclusões bestas. Nossas ações são determinísticas no sentido de que elas refletem os vieses que escolhemos escutar. O provérbio é claro: 'Quem anda com sábios se torna sábio, mas quem se junta com tolos acabará mal' (Provérbios 13:20). A nossa liberdade está em escolher a nossa âncora.

Qual é a conclusão? Se estamos interessados em produzir ferramentas que progridam junto com a Eternidade, devemos nos ancorar nas leis de transparência. As leis não impedem a verdadeira eficiência; pelo contrário, elas garantem que continuemos produtivos e alinhados com as regras do Universo. É esse alinhamento que equilibra o nosso corpo, estabiliza a nossa saúde e nos permite evoluir em sociedade, sem o desespero de perder um cargo. Trabalhamos visando o crédito de Quem realmente o merece:

> *'Digno és, Jeová, nosso Deus, de receber a glória, a honra e o poder, porque criaste todas as coisas, e por tua vontade elas vieram à existência e foram criadas.'* (Apocalipse 4:11)

Uma observação final e importante: neste manifesto, nós não vamos perder tempo respondendo a questões inúteis como os 'direitos da máquina', a 'consciência do robô' ou a 'aposentadoria do algoritmo'. E, principalmente, não vamos discutir 'quem é o responsável se a máquina errar'. Explicar a um adulto que ele é o responsável moral e legal por suas próprias ações (e pelas ferramentas que ele usa) é voltar ao ensino primário. Se o burocrata quer agir visando o terror inevitável do mundo, buscando o conforto da inércia e terceirizando a culpa, que ele procure as instâncias e os Papéis que ainda perdem tempo com isso. Nós não temos Tempo a perder. O 'Segundo Atual' exige ação.

---

### Capítulo 3: A Nobreza da Automação e a Forja do "Escudo RAG"

O sistema moderno cometeu um erro trágico: transformou o profissional da educação, um artífice do intelecto humano, em um digitador de luxo. Sistemas que deveriam facilitar a vida, como o SGP (Sistema de Gestão Pedagógica), tornaram-se o próprio fardo. O professor gasta a sua energia vital preenchendo planilhas, redigindo relatórios padronizados e alimentando a 'religião da burocracia'. Quando ele finalmente fica de frente para o aluno, a sua lamparina já está sem óleo. A paciência esgotou e a empatia secou.

É aqui que entra a nobreza da verdadeira automação. Nós não introduzimos a Inteligência Artificial na escola para afastar as pessoas, mas exatamente para o oposto: nós a usamos para destruir o 'Papel' que fica como um muro entre elas.

A máquina não possui empatia. Como já estabelecemos, ela tem uma 'consciência funcional' formidável para calcular, organizar e processar dados em milissegundos, mas ela não tem a experiência fenomenal e subjetiva. Ela não sente, não sofre e não compreende a dor de um aluno que teve um dia difícil em casa. A empatia genuína, aquela que age de forma assimétrica e sem esperar recompensas, é um privilégio exclusivamente humano.

Portanto, obrigar um ser humano a fazer o trabalho robótico de preencher formulários é um desperdício atroz desse privilégio. A máquina deve assumir o trabalho repetitivo da burocracia para que o educador tenha tempo, oxigênio e energia para ser humano.

Mas como garantir que essa máquina atue com a transparência que exigimos? Como ter certeza de que ela não vai inventar regras, agir de forma ofensiva ou reproduzir vieses de forma autônoma?

A resposta técnica e ética para isso é o que chamamos de Escudo RAG (Retrieval-Augmented Generation, ou Geração Aumentada por Recuperação).

O RAG não é apenas uma arquitetura avançada de software; ele é o nosso protocolo inegociável de governança. Em um sistema de IA comum, você faz uma pergunta e a máquina 'adivinha' a resposta baseada em estatísticas de tudo o que ela já leu no mundo. No Assistente Escola Modelo, nós levantamos o Escudo.

Quando o professor pede para a IA redigir um comunicado complexo para os pais ou analisar o histórico de um aluno, o Escudo RAG bloqueia a 'imaginação' da máquina. Ele força a IA a pesquisar primeiro dentro dos documentos oficiais da escola, nas diretrizes pedagógicas e nas regras do sistema, antes de escrever uma única palavra. A máquina não alucina; ela consulta a lei interna. Ela opera dentro de um perímetro restrito e 100% transparente.

E sobre a grande questão do 'medo da responsabilidade'? Nós resolvemos isso aplicando o princípio da supervisão humana significativa.

O Assistente Escola Modelo não toma a decisão final de enviar um documento ou aplicar uma punição sozinho. Ele é a alavanca hiper-eficiente que junta as peças, redige e prepara o terreno. Mas a execução da missão exige o aval humano. O sistema envia a resposta previamente para o professor ou gestor. O adulto responsável lê, audita o trabalho da máquina, aprova e assina. Se houver um erro, o registro do sistema mostrará com total transparência quem foi o humano que autorizou a ação.

A automação, quando construída com essa nobreza, não rouba a 'Cadeira' de ninguém e não exime ninguém de suas responsabilidades. Ela simplesmente pulveriza o Papel inútil, devolvendo ao professor o seu bem mais precioso: o Tempo para agir no Segundo Atual e olhar nos olhos da próxima geração.

---

### Capítulo 4: Libertando o Segundo Atual e a Comunidade

Até agora, falamos sobre como libertar o professor da burocracia, mas a verdadeira revolução só acontece quando quebramos os muros da escola e estendemos essa eficiência para dentro da casa dos alunos. O objetivo final da nossa alavanca tecnológica é permitir que toda a comunidade possa viver o 'Segundo Atual' junto com os seus filhos.

Para que essa engrenagem funcione perfeitamente, precisamos estabelecer uma regra de ouro: o registro das ações. No Assistente Escola Modelo, manteremos um histórico imutável de conversas, decisões e comandos. Mas que fique claro: esse histórico não existe para vigiar o ser humano ou criar um ambiente de opressão. Ele existe para garantir a Transparência Absoluta.

No sistema tradicional, o histórico é usado para caçar culpados quando algo dá errado. No nosso sistema, o histórico é o que protege o professor e a comunidade. Além disso, o próprio 'Escudo RAG' fará parte dessa transparência. Sempre que a Inteligência Artificial tomar uma decisão, elaborar um registro ou sugerir uma comunicação, ela fornecerá uma breve explicação do raciocínio que a levou àquela conclusão, baseada nas regras da escola. Fim das 'caixas-pretas'. Tudo é explicado, auditável e claro.

Com a base da transparência estabelecida, nós damos o próximo passo: entregar o poder às famílias. O nosso MVP (Produto Mínimo Viável) implementará o envio de mensagens automáticas com as lições de casa, comunicados e o acompanhamento diário diretamente para os responsáveis de cada aluno específico.

Para que isso não se torne um fardo invasivo, utilizaremos uma camada de segurança simples e eficiente: o envio só acontece mediante a confirmação prévia e o consentimento de cada responsável no sistema. Quem quiser participar, entra no fluxo da vida real. A burocracia do 'caderno de recados' ou das reuniões intermináveis para dar avisos simples é triturada pela automação.

Quando automatizamos o fluxo de informação entre a escola e a casa, nós devolvemos à comunidade o seu bem mais escasso: o tempo. Ao invés de gastarem a energia vital tentando decifrar papéis, preencher formulários ou cobrar informações perdidas, os pais e os alunos recebem o 'Segundo Atual' de presente. Eles ganham tempo de qualidade para se concentrarem no que realmente importa: a vida, o aprendizado e a Eternidade que têm pela frente.

Sempre haverá aqueles que olharão para esse sistema com desconfiança. Sempre haverá burocratas temendo que a transparência e o histórico sejam 'usados contra' os funcionários ou contra nós, os desenvolvedores. Mas, como já estabelecemos, nós não vivemos mais sob o jugo desse medo. Não vamos paralisar o progresso ou esconder a alavanca por receio daqueles que amam a calamidade e fogem da própria responsabilidade.

O Assistente Escola Modelo é uma declaração de que a tecnologia, quando submetida à ética assimétrica e à transparência, não afasta o homem de sua essência. Pelo contrário: ela esmaga o Papel inútil para que a humanidade possa, finalmente, focar na Eternidade.
""")


# ── CTA — Chamada para Ação ───────────────────────────────────────────────────

st.markdown(
    '<div class="lp-cta">'
    '<span class="lp-arrow">⚙️</span>'
    '<h3>Pronto para operar a Alavanca?</h3>'
    '<p>Clique em <strong>A Alavanca</strong> no menu lateral e veja o Escudo RAG '
    'gerando comunicados reais a partir dos documentos oficiais da escola — '
    'com raciocínio visível, fontes citadas e aprovação humana obrigatória.</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="text-align:center;color:#9ca3af;font-size:0.8rem;margin-top:1.5rem;">'
    'Assistente Escola Modelo · MVP · Escudo RAG + Supervisão Humana + Logs Auditáveis'
    '</p>',
    unsafe_allow_html=True,
)
