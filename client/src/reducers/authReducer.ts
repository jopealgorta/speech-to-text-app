import { LOGIN_FAILED, LOGIN_REQUEST, LOGIN_SUCCESS } from '../actions/types';

export const authReducer = (state = { user: null }, action: any) => {
	switch (action.type) {
		case LOGIN_REQUEST:
			return { loading: true };
		case LOGIN_SUCCESS:
			return { loading: false, user: action.payload };
		case LOGIN_FAILED:
			return { loading: false, error: action.payload };
		default:
			return state;
	}
};
