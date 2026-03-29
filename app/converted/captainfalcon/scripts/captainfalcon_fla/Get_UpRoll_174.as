package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpRoll_174 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Get_UpRoll_174()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame12():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

