package
{
    import flash.geom.Point;

    public class KirbyFinalSmashFoe
    {

        internal const CAPTURE_RANGE_ITEM:Number = 300.0;
        internal const CAPTURE_RANGE_LOW:Number = 150.0;
        internal const CAPTURE_RANGE_MED:Number = 250.0;
        internal const CAPTURE_RANGE_HIGH:Number = 350.0;
        internal const DAMAGE_THRESHOLD_LOW:Number = 0.0;
        internal const DAMAGE_THRESHOLD_MED:Number = 50.0;
        internal const DAMAGE_THRESHOLD_HIGH:Number = 100.0;
        internal const GRAVITY:Number = 2.0;
        internal const ARC_OFFSET:Number = 120.0;
        internal const CAPTURE_X_OFFSET:Number = 45.0;
        internal const CAPTURE_Y_OFFSET:Number = -10.0;
        internal const ARC_X_TIME:int = 25;
        internal const ARC_Y_TIME:int = 30;
        internal const FAILSAFE_TIME:int = 45;
        internal var state:int;
        internal var kirby:*;
        internal var foe:*;
        internal var forceTimer:FrameTimer;
        internal var startLocation:Point;
        internal var centerLocation:Point;
        internal var endLocation:Point;
        internal var arcTimer:FrameTimer;
        internal var arcXSpeed:Number;
        internal var arcYSpeed:Number;

        public function KirbyFinalSmashFoe(_arg_1:*, _arg_2:*):void
        {
            this.kirby = _arg_1;
            this.foe = _arg_2;
            this.forceTimer = new FrameTimer(this.FAILSAFE_TIME);
            this.arcTimer = new FrameTimer(this.ARC_Y_TIME);
            this.startLocation = new Point(_arg_2.getX(), _arg_2.getY());
            this.endLocation = new Point(((_arg_1.isFacingRight()) ? (_arg_1.getX() + this.CAPTURE_X_OFFSET) : (_arg_1.getX() - this.CAPTURE_X_OFFSET)), (_arg_1.getY() + this.CAPTURE_Y_OFFSET));
            this.centerLocation = new Point((_arg_2.getX() + ((this.endLocation.x - _arg_2.getX()) / 2)), ((_arg_2.getY() < this.endLocation.y) ? (_arg_2.getY() - this.ARC_OFFSET) : (this.endLocation.y - this.ARC_OFFSET)));
            var _local_3:Number = this.CAPTURE_RANGE_ITEM;
            if (_arg_2.getType() === "SSF2Character")
            {
                if (_arg_2.getDamage() <= this.DAMAGE_THRESHOLD_LOW)
                {
                    _local_3 = this.CAPTURE_RANGE_LOW;
                }
                else if (_arg_2.getDamage() <= this.DAMAGE_THRESHOLD_MED)
                {
                    _local_3 = this.CAPTURE_RANGE_MED;
                }
                else if (_arg_2.getDamage() <= this.DAMAGE_THRESHOLD_HIGH)
                {
                    _local_3 = this.CAPTURE_RANGE_HIGH;
                };
            };
            if (Point.distance(new Point(_arg_2.getX(), _arg_2.getY()), this.endLocation) <= _local_3)
            {
                this.state = 0;
                this.arcXSpeed = ((this.endLocation.x - this.startLocation.x) / this.ARC_X_TIME);
                this.arcYSpeed = -(Math.sqrt(((2 * this.GRAVITY) * (this.startLocation.y - this.centerLocation.y))));
                if (_arg_2.getType() === "SSF2Character")
                {
                    _arg_2.grab(_arg_1.getUID(), false, false, true);
                    if (!_arg_2.inState(CState.CAUGHT))
                    {
                        this.state = -1;
                    };
                }
                else if ((_arg_2.getType() === "SSF2Item") && _arg_2.inState(IState.IDLE))
                {
                    _arg_2.setXSpeed(0);
                    _arg_2.setYSpeed(0);
                    _arg_2.updateItemStats({
                        "ghost":true,
                        "gravity":0,
                        "canPickup":false,
                        "canReceiveDamage":false,
                        "canReceiveKnockback":false,
                        "canReceiveHits":false
                    });
                };
            }
            else
            {
                this.state = -1;
            };
        }

        private function moveFoe():void
        {
            this.foe.setX((this.startLocation.x + (this.arcXSpeed * this.arcTimer.elapsedFrames)));
            this.foe.setY((this.foe.getY() + this.arcYSpeed));
            this.arcYSpeed += this.GRAVITY;
            this.arcTimer.tick();
            this.forceTimer.tick();
            if ((this.arcYSpeed >= 0) && ((Point.distance(new Point(this.foe.getX(), this.foe.getY()), this.endLocation) < 50) || this.forceTimer.completed))
            {
                if (this.forceTimer.completed)
                {
                    this.foe.setX(this.endLocation.x);
                    this.foe.setY(this.endLocation.y);
                };
                this.state = 1;
                if (this.foe.getType() === "SSF2Character")
                {
                    this.foe.setVisibility(false);
                }
                else if (this.foe.getType() === "SSF2Item")
                {
                    this.foe.destroy();
                };
            };
        }

        public function isCooking():Boolean
        {
            return this.state === 1;
        }

        public function isBroken():Boolean
        {
            return this.state === -1;
        }

        public function isReleased():Boolean
        {
            if (!(this.foe) || this.foe.isDisposed() || !(this.foe.inState(CState.CAUGHT)))
            {
                return true;
            };
            return false;
        }

        public function update():void
        {
            var _local_1:Number = NaN;
            var _local_2:Number = NaN;
            if (this.kirby.isDisposed() || this.kirby.isStandby() || this.foe.isDisposed() || ((this.foe.getType() === "SSF2Character") && this.foe.isStandby()))
            {
                this.state = -1;
            };
            if (this.state === -1)
            {
            }
            else if (this.state === 0)
            {
                this.moveFoe();
            }
            else if (this.state === 1)
            {
                if (this.foe && (this.foe.getType() === "SSF2Character") && !(this.foe.inState(CState.CAUGHT)))
                {
                    if (SSF2API.hitTestGround(this.foe.getX(), this.foe.getY()))
                    {
                        _local_1 = (this.foe.getX() - this.kirby.getX());
                        _local_2 = (this.foe.getY() - this.kirby.getY());
                        this.foe.setX(this.kirby.getX());
                        this.foe.setY(this.kirby.getY());
                        this.foe.safeMove(_local_1, _local_2);
                    };
                    this.foe.setVisibility(true);
                    this.state = 2;
                };
            }
            else if (this.state === 2)
            {
            };
        }


    }
}

