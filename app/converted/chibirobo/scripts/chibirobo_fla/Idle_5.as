package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_5 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var rand:int;
        public var repeats:int;

        public function Idle_5()
        {
            super();
            addFrameScript(0, this.frame1, 59, this.frame60, 64, this.frame65, 219, this.frame220, 223, this.frame224);
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
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
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
                    this.gotoAndStop("bored");
                };
            };
            if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame60():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame65():*
        {
            this.self.playSound("chibi_DStep");
        }

        internal function frame220():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame224():*
        {
            gotoAndStop("loop");
        }


    }
}

