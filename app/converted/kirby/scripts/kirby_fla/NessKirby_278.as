package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class NessKirby_278 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var proj:Object;
        public var speed:Number;
        public var accel:Number;
        public var max:Number;
        public var hatCharge:Boolean;

        public function NessKirby_278()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 8, this.frame9, 12, this.frame13, 13, this.frame14, 20, this.frame21, 47, this.frame48, 48, this.frame49, 69, this.frame70);
        }

        public function projIsDead():Boolean
        {
            return !(this.proj) || this.proj.isDisposed() || this.proj.inState(PState.DEAD);
        }

        public function steer():void
        {
            SSF2API.print((this.proj == null).toString());
            if (!this.projIsDead())
            {
                if (this.self.getControls().RIGHT && !this.self.getControls().LEFT && (this.speed < this.max))
                {
                    this.speed += this.accel;
                }
                else if (this.self.getControls().LEFT && (this.speed > -(this.max)))
                {
                    this.speed -= this.accel;
                };
                this.proj.setXSpeed(this.speed);
            };
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_light", {
                "x":this.self.flipX(30),
                "y":5
            });
            this.self.attachEffect("ness_spark", {
                "x":(SSF2API.randomInteger(10, 0) - 5),
                "y":-(SSF2API.randomInteger(8, 35))
            });
        }

        public function killProj(_arg_1:*=null):*
        {
            if (!this.projIsDead())
            {
                this.proj.getStanceMC().gotoAndStop("fail");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.speed = 0.3;
            this.accel = 0.15;
            this.max = 5;
            this.hatCharge = false;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("global_sparkle", {
                    "x":this.self.flipX(30),
                    "y":-30
                });
                this.self.attachEffect("ness_shockwave");
                this.self.setYSpeed(0);
                this.self.setXSpeed((this.self.getXSpeed() * 0.65));
                this.self.playVoiceSound(1);
                this.self.pkflash = true;
                this.speed = this.self.flipX(0.3);
                this.self.setupHatEffect(1, -34, -43);
            };
        }

        internal function frame5():*
        {
            this.self.createTimer(7, -1, this.effects);
            this.self.attachEffect("ness_pkflasheffect");
        }

        internal function frame9():*
        {
            this.self.fireProjectile("ness_pkflash", 0, 25);
            this.proj = this.self.getCurrentProjectile();
            this.self.createTimer(1, -1, this.steer);
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.killProj, {"persistent":true});
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.killProj, {"persistent":true});
        }

        internal function frame13():*
        {
            if (this.self.getControls().BUTTON1 && !(this.projIsDead()))
            {
                gotoAndStop("charging");
            };
        }

        internal function frame14():*
        {
            this.self.destroyTimer(this.steer);
            this.self.destroyTimer(this.effects);
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.killProj);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.killProj);
            if (!this.proj.inState(PState.DEAD))
            {
                this.proj.getStanceMC().gotoAndStop("boom");
            };
        }

        internal function frame21():*
        {
            this.self.playSound("pkflash2");
            this.self.attachEffect("global_dust_cloud");
            this.self.attachEffect("ness_pkflasheffect2");
        }

        internal function frame48():*
        {
            this.self.endAttack();
        }

        internal function frame49():*
        {
            this.self.destroyTimer(this.effects);
            this.self.attachEffect("global_dust_cloud");
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.killProj);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.killProj);
        }

        internal function frame70():*
        {
            this.self.endAttack();
        }


    }
}

