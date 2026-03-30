package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class YoshiKirby_305 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var grounded:Boolean;
        public var continuePlaying:Boolean;

        public function YoshiKirby_305()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 20, this.frame21, 21, this.frame22, 25, this.frame26, 33, this.frame34, 36, this.frame37, 37, this.frame38);
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.grounded = true;
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.grounded = false;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.continuePlaying = false;
                if (this.self.isOnGround())
                {
                    this.grounded = true;
                }
                else
                {
                    this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                };
            };
        }

        internal function frame9():*
        {
            this.self.playVoiceSound(1);
            this.self.playAttackSound(1);
            if (this.grounded)
            {
                this.self.attachEffect("global_dust_light");
            };
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.stancePlayFrame("grabbed");
            };
        }

        internal function frame10():*
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.stancePlayFrame("grabbed");
            };
        }

        internal function frame11():*
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.stancePlayFrame("grabbed");
            };
        }

        internal function frame12():*
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.stancePlayFrame("grabbed");
            };
        }

        internal function frame13():*
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.stancePlayFrame("grabbed");
            };
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            this.self.swapDepthsWithGrabbedOpponent(true);
            this.self.playAttackSound(2);
        }

        internal function frame26():*
        {
            this.self.getGrabbedOpponent().getMC().visible = false;
        }

        internal function frame34():*
        {
            this.self.playVoiceSound(2);
            this.self.playAttackSound(3);
        }

        internal function frame37():*
        {
        }

        internal function frame38():*
        {
            this.self.endAttack();
        }


    }
}

