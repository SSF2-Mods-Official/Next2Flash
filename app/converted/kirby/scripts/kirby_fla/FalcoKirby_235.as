package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class FalcoKirby_235 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var end:*;
        public var canContinue:*;
        public var buttonReleased:Boolean;
        public var readyNext:Boolean;
        public var controls:Object;

        public function FalcoKirby_235()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 16, this.frame17, 22, this.frame23, 26, this.frame27, 28, this.frame29, 29, this.frame30, 34, this.frame35, 41, this.frame42, 46, this.frame47, 50, this.frame51, 52, this.frame53);
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
                gotoAndPlay("ground_loop");
            };
        }

        public function airContinueCombo():void
        {
            this.updateControls();
            if (this.end)
            {
                this.self.destroyTimer(this.airContinueCombo);
            }
            else if (this.canContinue && this.readyNext)
            {
                this.readyNext = false;
                this.buttonReleased = false;
                this.canContinue = false;
                gotoAndPlay("air_loop");
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
                if (!this.self.isOnGround())
                {
                    gotoAndPlay("air");
                };
                this.buttonReleased = false;
                this.readyNext = false;
                this.controls = this.self.getControls();
                this.self.createTimer(1, -1, this.continueCombo);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toIdle);
            };
        }

        internal function frame2():*
        {
            if (parent && SSF2API.isReady() && this.self && this.self.isCPU())
            {
                if ((this.self.getCPUAction() < 10) && (this.self.getCPUAction() > 0) && (this.self.getCPULevel() >= 7) && this.self.isOnGround())
                {
                    this.self.importCPUControls([128, 1, 0, 2, 64, 1, 0, 5, 1024, 1, 64, 1, 0, 1]);
                    this.self.setAttackEnabled(false, "b", 10);
                    this.self.endAttack();
                };
            };
        }

        internal function frame11():*
        {
            this.self.attachEffect("falco_blasterEffect", {
                "x":this.self.flipX(-15),
                "y":10
            });
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-18
            });
            this.self.attachEffect("global_dust_heavy", {
                "x":this.flipX(20),
                "scaleX":0.7,
                "scaleY":0.3
            });
            this.self.fireProjectile("falco_laser");
            this.self.playAttackSound(1);
        }

        internal function frame17():*
        {
            this.canContinue = true;
        }

        internal function frame23():*
        {
            this.canContinue = false;
            this.end = true;
        }

        internal function frame27():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }

        internal function frame30():*
        {
            this.end = false;
            this.canContinue = false;
            if (SSF2API.isReady() && this.self)
            {
                this.buttonReleased = false;
                this.readyNext = false;
                this.controls = this.self.getControls();
                this.self.destroyTimer(this.continueCombo);
                this.self.createTimer(1, -1, this.airContinueCombo);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toIdle);
            };
        }

        internal function frame35():*
        {
            this.self.attachEffect("falco_blasterEffect", {
                "x":this.self.flipX(-15),
                "y":10
            });
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-18
            });
            this.self.fireProjectile("falco_laser", 0, 15);
            this.self.playAttackSound(1);
        }

        internal function frame42():*
        {
            this.canContinue = true;
        }

        internal function frame47():*
        {
            this.canContinue = false;
            this.end = true;
        }

        internal function frame51():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame53():*
        {
            this.self.endAttack();
        }


    }
}

