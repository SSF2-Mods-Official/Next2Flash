package
{
    import flash.display.MovieClip;

    public class InhaleController
    {

        public var SWALLOW_TIMEOUT:int = 120;
        public var SWALLOW_TIMEOUT_SELF_X_SPEED:Number = -9.0;
        public var SWALLOW_TIMEOUT_FOE_Y_SPEED:Number = -8.0;
        public var INHALE_SPEED_CAP_GROUND:Number = 4.0;
        public var INHALE_SPEED_CAP_AIR:Number = 6.2;
        public var spitTimeout:int;
        private var _state:int;
        private var character:SSF2Character;
        public var spitInterrupt:Function;
        public var grabHook:Function;
        public var cleanupHook:Function;
        public var bulletStatsName:String = "kirby_starbullet";

        public function InhaleController(_arg_1:SSF2Character):void
        {
            this.character = _arg_1;
            this.spitTimeout = this.SWALLOW_TIMEOUT;
            this._state = InhaleState.INACTIVE;
            this.character.addEventListener(SSF2Event.STATE_CHANGE, this.handleInhaleStateChange, {"persistent":true});
        }

        public function update():*
        {
            var _local_3:* = undefined;
            var _local_4:* = undefined;
            if (this._state === InhaleState.INACTIVE)
            {
                return;
            }
            else
            if (this._state !== InhaleState.SPIT)
            {
                _local_3 = this.character.getGrabbedOpponents()[0];
                if (_local_3 == null)
                {
                    this.setState(InhaleState.INACTIVE);
                    this.character.grabRelease();
                    return;
                };
                _local_3.setX(this.character.getX());
                _local_3.setY(this.character.getY());
                this.spitTimeout--;
                _local_4 = _local_3.getControls(true);
                if (_local_4.BUTTON1 || _local_4.BUTTON2)
                {
                    this.spitTimeout -= 10;
                };
                if (_local_4.UP || _local_4.DOWN || _local_4.LEFT || _local_4.RIGHT)
                {
                    this.spitTimeout -= 10;
                };
                if (this.spitTimeout <= 0)
                {
                    this.setState(InhaleState.SPIT);
                    return;
                };
            };
            var _local_1:* = this.character.getControls();
            var _local_2:* = this.character.getControls(true);
            switch (_local_5)
            {
            case InhaleState.IDLE:
            this.setState(InhaleState.FALL);
            this.setState(InhaleState.SQUAT);
            this.setState(InhaleState.WALK);
            this.setState(InhaleState.TURN);
            break;
            case InhaleState.WALK:
            this.setState(InhaleState.FALL);
            this.setState(InhaleState.SQUAT);
            this.setState(InhaleState.IDLE);
            this.setState(InhaleState.TURN);
            break;
            case InhaleState.JUMP:
            case InhaleState.FALL:
            this.setState(InhaleState.LAND);
            break;
            case InhaleState.TURN:
            this.setState(InhaleState.FALL);
            case 5:
            default:
            break;
            }
        }

        public function start():*
        {
            this.character.addEventListener(SSF2Event.CHAR_GRAB, this.onGrab, {"persistent":true});
            this.character.addEventListener(SSF2Event.STATE_CHANGE, this.eventCleanup, {"persistent":true});
            this.spitTimeout = this.SWALLOW_TIMEOUT;
        }

        private function handleInhaleStateChange(_arg_1:*):void
        {
            this.setState(InhaleState.INACTIVE);
        }

        public function setState(_arg_1:int):void
        {
            var _local_3:MovieClip;
            if (this._state === _arg_1)
            {
                return;
            };
            var _local_2:int = this._state;
            this._state = _arg_1;
            SSF2API.print(((("going from " + _local_2) + " to ") + this._state));
            switch (this._state)
            {
            case InhaleState.INACTIVE:
            this.character.destroyTimer(this.checkSpit);
            break;
            case InhaleState.IDLE:
            this.character.updateAttackStats({
                "xSpeedCap":(this.INHALE_SPEED_CAP_GROUND * 0.5),
                "cancelWhenAirborne":false,
                "allowControl":true
            });
            this.character.stancePlayFrame("inhale_hold_idle");
            break;
            case InhaleState.WALK:
            this.character.stancePlayFrame("inhale_hold_walk");
            break;
            case InhaleState.JUMP:
            break;
            case InhaleState.FALL:
            this.character.updateAttackStats({"xSpeedCap":(this.INHALE_SPEED_CAP_AIR * 0.5)});
            this.character.stancePlayFrame("inhale_hold_fall");
            break;
            case InhaleState.LAND:
            this.character.updateAttackStats({
                "allowControl":false,
                "xSpeedCap":(this.INHALE_SPEED_CAP_GROUND * 0.5)
            });
            _local_3 = SSF2API.attachEffectOverlay("effect_land");
            _local_3.width *= this.character.getSizeRatio();
            _local_3.height *= this.character.getSizeRatio();
            _local_3.alpha = 0.75;
            _local_3.scaleX *= -1;
            _local_3.x = (this.character.getX() + SSF2API.getStage().getMidground().x);
            _local_3.y = (this.character.getY() + SSF2API.getStage().getMidground().y);
            this.character.stancePlayFrame("inhale_hold_land");
            break;
            case InhaleState.SPIT:
            this.character.destroyTimer(this.checkSpit);
            this.character.updateAttackStats({"allowControl":false});
            this.character.stancePlayFrame("spit");
            break;
            case InhaleState.SQUAT:
            this.character.updateAttackStats({"xSpeedCap":(this.INHALE_SPEED_CAP_AIR * 0.5)});
            this.character.stancePlayFrame("inhale_hold_jump");
            break;
            case InhaleState.GRAB:
            this.character.updateAttackStats({"allowControl":false});
            this.character.stancePlayFrame("inhale_hold_grabbed");
            break;
            case InhaleState.TURN:
            this.character.updateAttackStats({"allowControl":false});
            this.character.stancePlayFrame("inhale_turn");
            break;
            case 10:
            default:
            this._state = _local_2;
            throw new Error("Invalid inhale state!");
            break;
            }
        }

        private function onGrab(_arg_1:*):*
        {
            this.character.removeEventListener(SSF2Event.CHAR_GRAB, this.onGrab);
            this.character.removeEventListener(SSF2Event.STATE_CHANGE, this.eventCleanup);
            var _local_2:* = this.character.getGrabbedOpponents()[0];
            _local_2.grab(this.character.getUID(), false, true, true);
            _local_2.setVisibility(false);
            this.setState(InhaleState.GRAB);
            this.character.createTimer(1, -1, this.checkSpit);
            if (this.grabHook != null)
            {
                this.grabHook();
            };
        }

        private function eventCleanup(_arg_1:*):*
        {
            this.character.removeEventListener(SSF2Event.CHAR_GRAB, this.onGrab);
            this.character.removeEventListener(SSF2Event.STATE_CHANGE, this.eventCleanup);
            if (this.cleanupHook != null)
            {
                this.cleanupHook();
            };
        }

        private function checkSpit():*
        {
            if ((this._state === InhaleState.INACTIVE) || (this._state === InhaleState.SPIT) || (this._state === InhaleState.LAND) || (this._state === InhaleState.GRAB) || ((this.spitInterrupt != null) && this.spitInterrupt()))
            {
                return;
            };
            var _local_1:* = this.character.getControls(true);
            if (_local_1.BUTTON1 || _local_1.BUTTON2)
            {
                this.setState(InhaleState.SPIT);
            };
        }

        public function spitFoe():*
        {
            var _local_2:* = undefined;
            var _local_1:* = this.character.getGrabbedOpponents()[0];
            if (_local_1)
            {
                this.character.releaseOpponent();
                _local_2 = this.character.fireProjectile(this.bulletStatsName, 0, -6);
                if (_local_2)
                {
                    _local_2.grabFoe(SSF2Utils.cast(_local_1));
                };
            };
        }

        public function getState():int
        {
            return this._state;
        }


    }
}

