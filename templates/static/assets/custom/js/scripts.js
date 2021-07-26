(function () {
    const select_variacao = document.getElementById('select-variacoes');
    const variation_preco = document.getElementById('variation-preco');
    const variation_preco_muted = document.getElementById('variation-preco-muted');

    if (!select_variacao || !variation_preco) {
        return;
    }

    const atualiza_preco = () => {
        const preco = select_variacao.options[select_variacao.selectedIndex].getAttribute('data-preco');
        const preco_promocional = select_variacao.options[select_variacao.selectedIndex].getAttribute('data-preco-promocional');

        if (preco_promocional) {
            variation_preco.innerHTML = preco_promocional;
            variation_preco_muted.innerHTML = preco;
        } else {
            variation_preco.innerHTML = preco;
            variation_preco_muted.innerHTML = '';
        }
    }
    atualiza_preco();
    
    select_variacao.addEventListener('change', function () {
        atualiza_preco();
    });
})();

