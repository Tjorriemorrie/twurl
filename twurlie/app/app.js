import './theme';
import { router, route } from 'reapp-kit';

router(require,
	route('index', '/',
		route('auth')
	)
);
