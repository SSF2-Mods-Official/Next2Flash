package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Fall_18 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Fall_18()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("redo");
            };
        }

        internal function frame7():*
        {
            this.self.stancePlayFrame("redo");
        }


    }
}

