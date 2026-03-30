package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class SheikKirbyAir_298 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var num_needles:int;
        public var xframe:*;
        public var charge:*;
        public var thrown:Boolean;
        public var rand:*;
        public var proj:*;

        public function SheikKirbyAir_298()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 14, this.frame15, 15, this.frame16, 19, this.frame20, 20, this.frame21, 21, this.frame22, 30, this.frame31);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function land(_arg_1:*=null):*
        {
            SSF2API.print(this.thrown.toString());
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("kirby_land2");
            };
            if (!this.thrown)
            {
                SSF2API.print("ding");
                this.self.forceAttack("kirby_sheik", currentFrame, true);
            }
            else
            {
                SSF2API.print("ding2");
                this.self.forceAttack("kirby_sheik", (currentFrame + 1), true);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.thrown = false;
            this.rand = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
            };
        }

        internal function frame7():*
        {
            this.xframe = "charging";
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame16():*
        {
            this.self.playVoiceSound(1);
            this.xframe = "attack";
            this.charge = this.self.getAttackStat("chargetime");
            this.num_needles = ((this.charge / 10) + 1);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toIdle);
        }

        internal function frame20():*
        {
            this.num_needles--;
            this.self.fireProjectile("airneedle", this.self.getXSpeed(), this.self.getYSpeed());
            this.thrown = true;
        }

        internal function frame21():*
        {
            if (this.num_needles <= 0)
            {
                this.self.stancePlayFrame("finish");
            }
            else
            {
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame22():*
        {
            this.thrown = false;
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

