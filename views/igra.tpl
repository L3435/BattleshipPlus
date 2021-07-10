% rebase("menu.tpl")

<style>
	table {
		width: 350px;
		height: 350px;
		margin-left: auto;
		margin-right: auto;
	}

	td {
		width: 35px;
	}

	tr {
		height: 35px;
	}

	.prazna:hover {
		background-color: azure;
	}

	.zgresena {
		background-color: blue;
	}

	.zadeta {
		background-color: crimson;
	}

	.potopljena {
		background-color: gray;
	}
</style>

<section class="section">
  <div class="columns">
    <div class="column">
		<table class="table is-bordered">
			% for x in range(10):
			<tr>
				% for y in range(10):
				% if igra.radar[x][y] == ' ':
				<td class="prazna" style="padding: 0 0 0 0;">
					<a href="/igra/?{{x}}&{{y}}" style="display:block;width:100%;height:100%;">
						&nbsp;
					</a>
				</td>
				% elif igra.radar[x][y] == '.':
				<td class="zgresena" style="padding: 0 0 0 0;">
					<div style="display:block;width:100%;height:100%;">
						&nbsp;
					</div>
				</td>
				% elif igra.radar[x][y] == 'x':
				<td class="zadeta" style="padding: 0 0 0 0;">
					<div style="display:block;width:100%;height:100%;">
						&nbsp;
					</div>
				</td>
				% elif igra.radar[x][y] == 'P':
				<td class="potopljena" style="padding: 0 0 0 0;">
					<div style="display:block;width:100%;height:100%;">
						&nbsp;
					</div>
				</td>
				% end
				% end
			</tr>
			% end
		</table>
    </div>
    <div class="column">
      Second column
    </div>
  </div>
</section>