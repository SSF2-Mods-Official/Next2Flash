package chibirobo_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class Telly_Dummy__126 extends MovieClip
    {

        public var self:*;
        public var changeAnimationReady:*;
        public var shouldMove:Boolean;
        public var hasProjectile:Boolean;
        public var currentAnimation:*;
        public var character:*;
        public var targetCoors:Point;

        public function Telly_Dummy__126()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 8, this.frame9);
        }

        public function sendToEnd(_arg_1:*=null):void
        {
            this.character.setGlobalVariable("telly", null);
            this.self.destroyTimer(this.moveTelly);
            this.self.removeEventListener(SSF2Event.PROJ_DESTROYED, this.sendToEnd);
            this.self.removeEventListener(SSF2Event.CHAR_KO_POINT, this.sendToKoPoint);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.sendToDeath);
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.sendToHurt);
            this.self.destroy();
        }

        public function sendToKoPoint(_arg_1:*=null):void
        {
            if (this.changeAnimationReady)
            {
                this.self.stancePlayFrame("ko_point");
            };
        }

        public function sendToHurt(_arg_1:*=null):void
        {
            if (this.changeAnimationReady)
            {
                this.self.stancePlayFrame("hurt");
            };
        }

        public function sendToDeath(_arg_1:*=null):void
        {
            if (this.changeAnimationReady)
            {
                this.self.stancePlayFrame("death");
            };
        }

        public function sendToProjectile(_arg_1:*=null):void
        {
            if (this.changeAnimationReady && (this.currentAnimation != "projectile"))
            {
                this.self.stancePlayFrame("projectile");
            };
        }

        public function moveTelly():void
        {
            var _local_1:Number = NaN;
            var _local_2:Number = NaN;
            if ((this.character.getLives() == 0) || this.character.isStandby())
            {
                this.sendToEnd();
            }
            else
            {
                this.targetCoors = new Point(this.character.getX(), this.character.getY());
                this.targetCoors.y -= (this.character.getHeight() * 1.5);
                if (this.character.isFacingRight())
                {
                    this.targetCoors.x -= this.character.getWidth();
                }
                else
                {
                    this.targetCoors.x += this.character.getWidth();
                };
                _local_1 = ((this.targetCoors.x - this.self.getX()) / 10);
                _local_2 = ((this.targetCoors.y - this.self.getY()) / 10);
                if (this.shouldMove)
                {
                    this.self.setXSpeed(_local_1);
                    this.self.setYSpeed(_local_2);
                    this.self.setRotation(_local_1);
                }
                else
                {
                    this.self.setYSpeed(0);
                    this.self.setYSpeed(0);
                    this.self.setRotation(0);
                };
                if (_local_1 > 0.1)
                {
                    this.self.faceRight();
                }
                else if (_local_1 < -0.1)
                {
                    this.self.faceLeft();
                }
                else if (this.character.isFacingRight())
                {
                    this.self.faceRight();
                }
                else
                {
                    this.self.faceLeft();
                };
                if (this.hasProjectile)
                {
                    this.sendToProjectile();
                };
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.changeAnimationReady = true;
            this.shouldMove = true;
            this.hasProjectile = false;
            this.currentAnimation = "idle";
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                if (this.character)
                {
                    this.targetCoors = new Point(this.character.getX(), this.character.getY());
                    this.self.createTimer(1, -1, this.moveTelly, {"persistent":true});
                    this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.sendToEnd);
                    this.character.addEventListener(SSF2Event.CHAR_KO_POINT, this.sendToKoPoint, {"persistent":true});
                    this.character.addEventListener(SSF2Event.CHAR_HURT, this.sendToHurt, {"persistent":true});
                    this.character.addEventListener(SSF2Event.CHAR_KO_DEATH, this.sendToDeath, {"persistent":true});
                    this.self.swapDepths(this.character);
                };
            };
        }

        internal function frame2():*
        {
            this.changeAnimationReady = true;
            this.shouldMove = true;
            this.currentAnimation = "idle";
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("idle");
        }


    }
}

