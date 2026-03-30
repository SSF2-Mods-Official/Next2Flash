package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_3 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var rand:int;
        public var repeats:int;

        public function Idle_3()
        {
            super();
            addFrameScript(0, this.frame1, 22, this.frame23, 67, this.frame68, 71, this.frame72);
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
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.rand = 0;
            if (!this.repeats)
            {
                this.repeats = 0;
            };
            if (parent && SSF2API.isReady() && this.self && (this.repeats >= 3))
            {
                this.rand = SSF2API.randomInteger(0, 3);
                if (this.rand >= 3)
                {
                    this.repeats = 0;
                    gotoAndStop("wait");
                };
            };
            if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame23():*
        {
            this.repeats++;
            gotoAndStop("loop");
        }

        internal function frame68():*
        {
            gotoAndStop("loop");
        }

        internal function frame72():*
        {
            gotoAndStop("loop");
        }


    }
}

