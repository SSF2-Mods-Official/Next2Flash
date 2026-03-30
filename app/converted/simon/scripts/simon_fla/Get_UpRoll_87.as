package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpRoll_87 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Get_UpRoll_87()
        {
            super();
            addFrameScript(0, this.frame1, 13, this.frame14, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame14():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

