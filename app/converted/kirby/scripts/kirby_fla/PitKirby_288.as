package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class PitKirby_288 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var direction:String;
        public var charged:Boolean;
        public var timer:Number;
        public var timeMax:Number;
        public var damage:Number;
        public var damageMax:Number;
        public var damageMin:Number;
        public var powerMax:*;
        public var powerMin:*;
        public var fullCharge:Number;
        public var minCharge:Number;
        public var projY:Number;
        public var projX:Number;
        public var proj:Object;
        public var fired:Boolean;
        public var bowCharge:*;

        public function PitKirby_288()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 8, this.frame9, 9, this.frame10, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 17, this.frame18, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 28, this.frame29, 29, this.frame30, 30, this.frame31, 37, this.frame38, 43, this.frame44);
        }

        public function canFire():Boolean
        {
            return (this.direction != "mid") && (this.timer >= this.minCharge);
        }

        public function aim():void
        {
            var _local_1:Object = this.self.getControls();
            if ((this.timer >= this.minCharge) && !(this.fired))
            {
                if (_local_1.LEFT && this.self.isFacingRight() && this.canFire())
                {
                    this.self.faceLeft();
                }
                else if (_local_1.RIGHT && !(this.self.isFacingRight()) && this.canFire())
                {
                    this.self.faceRight();
                };
                if ((_local_1.UP && (this.direction == "down")) || (!(_local_1.UP) && (this.direction == "up")))
                {
                    this.self.stancePlayFrame(("aim" + this.direction));
                    this.direction = "mid";
                };
            };
        }

        public function fire(_arg_1:Number):void
        {
            this.fired = true;
            this.self.attachEffect("global_dust_heavy");
            this.self.attachEffect("global_dust_swirl");
            this.self.destroyTimer(this.aim);
            this.self.destroyTimer(this.checkRelease);
            this.proj.destroy();
            this.proj = this.self.fireProjectile("pit_arrow2", this.projX, this.projY);
            this.proj.getStanceMC().arrowAngle = _arg_1;
            this.proj.getStanceMC().curAngle = _arg_1;
            this.timer = Math.min(this.timer, this.fullCharge);
            this.proj.updateAttackBoxStats(1, {
                "damage":((((this.timer - this.minCharge) / (this.fullCharge - this.minCharge)) * (this.damageMax - this.damageMin)) + this.damageMin),
                "power":((((this.timer - this.minCharge) / (this.fullCharge - this.minCharge)) * (this.powerMax - this.powerMin)) + this.powerMin)
            });
        }

        public function checkRelease():void
        {
            this.proj.setX(((this.self.getX() + this.self.getXSpeed()) + this.self.flipX(this.projX)));
            this.proj.setY(((this.self.getY() + this.self.getYSpeed()) + this.projY));
            this.timer++;
            if (this.canFire() && ((this.timer > this.timeMax) || !this.self.getControls().BUTTON1))
            {
                if (this.direction == "up")
                {
                    this.fire(180);
                }
                else if (this.self.isFacingRight())
                {
                    this.fire(90);
                }
                else
                {
                    this.fire(270);
                };
                this.self.stancePlayFrame(("fire" + this.direction));
            };
            if ((this.timer > this.fullCharge) && !(this.charged))
            {
                this.self.attachEffect("global_sparkle", {"y":-20});
                this.charged = true;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.direction = "down";
            this.charged = false;
            this.timer = 0;
            this.timeMax = 120;
            this.damage = 5;
            this.damageMax = 11;
            this.damageMin = 2.5;
            this.powerMax = 58;
            this.powerMin = 8;
            this.fullCharge = 15;
            this.minCharge = 5;
            this.projY = -13;
            this.projX = -3;
            this.fired = false;
        }

        internal function frame3():*
        {
            this.self.fireProjectile("pit_arrow", this.self.flipX(this.projX), this.projY);
            this.proj = this.self.getCurrentProjectile();
            this.proj.faceRight();
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(180);
            };
        }

        internal function frame4():*
        {
            this.self.createTimer(1, -1, this.checkRelease);
            this.self.createTimer(1, -1, this.aim);
        }

        internal function frame5():*
        {
            this.direction = "down";
            this.proj.setRotation(0);
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(180);
            };
        }

        internal function frame6():*
        {
            this.bowCharge = this.self.playAttackSound(1);
        }

        internal function frame9():*
        {
            this.proj.setRotation(0);
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(180);
            };
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("hold");
        }

        internal function frame12():*
        {
            this.proj.setRotation(330);
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(210);
            };
        }

        internal function frame13():*
        {
            this.proj.setRotation(300);
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(240);
            };
        }

        internal function frame14():*
        {
            this.direction = "up";
            gotoAndStop("holdup");
        }

        internal function frame15():*
        {
            this.proj.setRotation(272);
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(268);
            };
        }

        internal function frame16():*
        {
            this.self.stancePlayFrame("holdup");
        }

        internal function frame18():*
        {
            this.proj.setRotation(300);
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(240);
            };
        }

        internal function frame19():*
        {
            this.proj.setRotation(330);
            if (!this.self.isFacingRight())
            {
                this.proj.setRotation(210);
            };
        }

        internal function frame20():*
        {
            this.direction = "down";
            gotoAndStop("hold");
        }

        internal function frame21():*
        {
            SSF2API.stopSound(this.bowCharge);
            this.self.playVoiceSound(1);
        }

        internal function frame22():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame29():*
        {
            this.self.stancePlayFrame("endlag");
        }

        internal function frame30():*
        {
            SSF2API.stopSound(this.bowCharge);
            this.self.playVoiceSound(1);
        }

        internal function frame31():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame38():*
        {
            this.self.stancePlayFrame("endlag");
        }

        internal function frame44():*
        {
            this.self.endAttack();
        }


    }
}

