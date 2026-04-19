// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemAssist_95

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemAssist_95 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function ItemAssist_95()
        {
            addFrameScript(0, this.frame1, 7, this.frame8, 30, this.frame31);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
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
}//package blackmage_fla

