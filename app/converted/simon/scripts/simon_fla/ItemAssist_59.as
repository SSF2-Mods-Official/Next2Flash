package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemAssist_59 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function ItemAssist_59()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame8():*
        {
            this.self.getItem().activateItem();
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

