package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_3 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var repeats:int;

        public function Idle_3()
        {
            super();
            addFrameScript(0, this.frame1, 20, this.frame21, 39, this.frame40, 40, this.frame41, 41, this.frame42, 63, this.frame64, 85, this.frame86);
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
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame21():*
        {
            if ((this.repeats >= 3) && (SSF2API.random() > 0.5))
            {
                this.repeats = 0;
                if (SSF2API.random() > 0.5)
                {
                    this.self.stancePlayFrame("wait1");
                }
                else
                {
                    this.self.stancePlayFrame("wait2");
                };
            };
        }

        internal function frame40():*
        {
            this.repeats++;
            gotoAndStop("loop");
        }

        internal function frame41():*
        {
            SSF2API.playSound("beep_crouch_2");
        }

        internal function frame42():*
        {
            gotoAndStop("loop");
        }

        internal function frame64():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame86():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

