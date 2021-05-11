import {
	IonContent,
	IonHeader,
	IonPage,
	IonTitle,
	IonToolbar,
	IonRow,
	IonCol,
	IonItem,
	IonInput,
	IonLabel,
	IonIcon,
	IonGrid,
	IonButton
} from '@ionic/react';
import { personCircle } from 'ionicons/icons';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useHistory } from 'react-router';
import { login } from '../actions/authActions';

const Login: React.FC = () => {
	let history = useHistory();
	const dispatch = useDispatch();
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');

	const onSubmit = (e: any) => {
		e.preventDefault();
		// TODO: Checks
		dispatch(login(email, password));
		history.push('/home');
	};

	return (
		<IonPage>
			<IonHeader>
				<IonToolbar>
					<IonTitle>Login</IonTitle>
				</IonToolbar>
			</IonHeader>
			<IonContent fullscreen>
				<form onSubmit={onSubmit}>
					<IonHeader collapse='condense'>
						<IonToolbar>
							<IonTitle size='large'>Login</IonTitle>
						</IonToolbar>
					</IonHeader>
					<IonGrid>
						<IonRow>
							<IonCol className='ion-text-center'>
								<IonIcon style={{ fontSize: '70px', color: '#0040ff' }} icon={personCircle} />
							</IonCol>
						</IonRow>
						<IonRow>
							<IonCol>
								<IonItem>
									<IonLabel position='floating'> Email</IonLabel>
									<IonInput
										type='email'
										value={email}
										onIonChange={(e: any) => setEmail(e.detail.value)}
									/>
								</IonItem>
							</IonCol>
						</IonRow>
						<IonRow>
							<IonCol>
								<IonItem>
									<IonLabel position='floating'> Password</IonLabel>
									<IonInput
										type='password'
										value={password}
										onIonChange={(e: any) => setPassword(e.detail.value)}
									/>
								</IonItem>
							</IonCol>
						</IonRow>
						<IonRow>
							<IonCol>
								<IonButton type='submit' expand='block'>
									Login
								</IonButton>
							</IonCol>
						</IonRow>
					</IonGrid>
				</form>
			</IonContent>
		</IonPage>
	);
};

export default Login;
