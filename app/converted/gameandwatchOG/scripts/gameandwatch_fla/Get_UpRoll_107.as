package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpRoll_107 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Get_UpRoll_107()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 5, this.frame6, 9, this.frame10, 13, this.frame14, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame4():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame6():*
        {
            this.self.playSound("gw_step1");
        }

        internal function frame10():*
        {
            this.self.setIntangibility(false);
            this.self.playSound("gw_step2");
        }

        internal function frame14():*
        {
            this.self.playSound("gw_step1");
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

