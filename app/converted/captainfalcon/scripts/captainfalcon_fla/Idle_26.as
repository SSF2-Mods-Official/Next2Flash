package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_26 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var rand:int;

        public function Idle_26()
        {
            super();
            addFrameScript(0, this.frame1, 46, this.frame47, 85, this.frame86, 89, this.frame90);
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
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.rand = 0;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 8)
                {
                    this.gotoAndStop("bored");
                };
            };
            if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame47():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame86():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame90():*
        {
            gotoAndStop("loop");
        }


    }
}

