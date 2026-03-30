package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_40 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Helpless_40()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                switch (this.self.getGlobalVariable("usedUpB"))
                {
                case "softfall":
                this.self.setGlobalVariable("usedUpB", "softland");
                break;
                case "hardfall":
                this.self.setGlobalVariable("usedUpB", "hardland");
                break;
                case 2:
                default:
                this.self.setGlobalVariable("usedUpB", "none");
                break;
                }
            };
        }

        internal function frame11():*
        {
            this.self.stancePlayFrame("back");
        }


    }
}

