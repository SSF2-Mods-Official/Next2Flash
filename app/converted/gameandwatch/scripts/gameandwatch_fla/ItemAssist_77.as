package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemAssist_77 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function ItemAssist_77()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 15, this.frame16, 26, this.frame27, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame8():*
        {
            this.self.getItem().activateItem();
        }

        internal function frame16():*
        {
            this.self.playSound("beep_jump");
        }

        internal function frame27():*
        {
            this.self.playSound("beep_dair_landing");
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

