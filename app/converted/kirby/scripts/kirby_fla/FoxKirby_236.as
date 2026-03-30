package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class FoxKirby_236 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var end:*;
        public var canContinue:*;
        public var buttonReleased:Boolean;
        public var readyNext:Boolean;
        public var controls:Object;

        public function FoxKirby_236()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 8, this.frame9, 17, this.frame18, 19, this.frame20, 20, this.frame21, 25, this.frame26, 28, this.frame29, 31, this.frame32, 33, this.frame34, 35, this.frame36);
        }

        public function updateControls():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.buttonReleased = true;
            };
            if (this.buttonReleased && this.controls.BUTTON1)
            {
                this.readyNext = true;
            };
        }

        public function continueCombo():void
        {
            this.updateControls();
            if (this.end)
            {
                this.self.destroyTimer(this.continueCombo);
            }
            else if (this.canContinue && this.readyNext)
            {
                this.readyNext = false;
                this.buttonReleased = false;
                this.canContinue = false;
                if (!this.self.isOnGround())
                {
                    gotoAndStop("loop2");
                }
                else
                {
                    gotoAndStop("loop");
                };
            };
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.end = false;
            this.canContinue = false;
            if (SSF2API.isReady() && this.self)
            {
                this.buttonReleased = false;
                this.readyNext = false;
                this.controls = this.self.getControls();
                this.self.createTimer(1, -1, this.continueCombo);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toIdle);
                if (!this.self.isOnGround())
                {
                    gotoAndStop("airstart");
                    this.self.updateAttackStats({
                        "allowControl":true,
                        "allowControlGround":false
                    });
                };
            };
        }

        internal function frame6():*
        {
            this.self.attachEffect("fox_blasterEffect", {"y":15});
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-13
            });
            this.self.attachEffect("global_dust_heavy", {
                "x":this.flipX(20),
                "scaleX":0.7,
                "scaleY":0.3
            });
            this.self.fireProjectile("laser", 30, -7);
            this.self.playAttackSound(1);
        }

        internal function frame9():*
        {
            this.canContinue = true;
        }

        internal function frame18():*
        {
            this.canContinue = false;
            this.end = true;
            this.self.playAttackSound(2);
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }

        internal function frame21():*
        {
            this.self.playAttackSound(2);
            this.self.endAttack();
        }

        internal function frame26():*
        {
            this.self.attachEffect("fox_blasterEffect", {"y":15});
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-13
            });
            this.self.fireProjectile("laser", 30, -7);
            this.self.playAttackSound(1);
        }

        internal function frame29():*
        {
            this.canContinue = true;
        }

        internal function frame32():*
        {
            this.canContinue = false;
            this.end = true;
            this.self.playAttackSound(2);
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }

        internal function frame36():*
        {
            this.self.playAttackSound(2);
            this.self.endAttack();
        }


    }
}

