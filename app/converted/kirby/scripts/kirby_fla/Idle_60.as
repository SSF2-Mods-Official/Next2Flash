package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_60 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var fatstand:*;
        public var idle_repeat:*;
        public var rand:int;
        public var repeats:int;

        public function Idle_60()
        {
            super();
            addFrameScript(0, this.frame1, 24, this.frame25, 75, this.frame76, 144, this.frame145, 145, this.frame146, 177, this.frame178, 179, this.frame180, 181, this.frame182);
        }

        public function uncrouch(_arg_1:*=null):*
        {
            if ((_arg_1.data.fromState == 12) && this.self.getGlobalVariable("crouchdown"))
            {
                this.self.setGlobalVariable("crouchdown", false);
                this.self.stancePlayFrame("uncrouch");
            }
            else
            {
                this.self.setGlobalVariable("crouchdown", false);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.fatstand = false;
            this.idle_repeat = 0;
            this.rand = 0;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
            };
            if (SSF2API.isReady() && this.self && (this.repeats >= 3))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 5)
                {
                    this.repeats = 0;
                    this.gotoAndStop("wait1");
                };
                if (this.rand >= 8)
                {
                    this.repeats = 0;
                    this.gotoAndStop("wait2");
                };
            };
            if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame25():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame76():*
        {
            gotoAndStop("loop");
        }

        internal function frame145():*
        {
            gotoAndStop("loop");
        }

        internal function frame146():*
        {
            this.fatstand = true;
        }

        internal function frame178():*
        {
            gotoAndStop("fatstand_loop");
        }

        internal function frame180():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.playSound("ssf2_snd_sfx_kirby_crouch_end");
            };
        }

        internal function frame182():*
        {
            gotoAndStop("loop");
        }


    }
}

