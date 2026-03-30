package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemRaise_69 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemRaise_69()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 7, this.frame8, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame4():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame5():*
        {
            this.self.updateAuraPaws();
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

