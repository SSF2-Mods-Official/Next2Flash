package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemAssist_91 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function ItemAssist_91()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame8():*
        {
            if (this.self.getItem())
            {
                this.self.getItem().activateItem();
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

