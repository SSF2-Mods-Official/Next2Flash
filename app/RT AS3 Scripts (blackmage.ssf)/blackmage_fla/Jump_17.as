// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Jump_17

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_17 extends MovieClip 
    {

        internal var hand:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:*;
        internal var done:*;

        public function Jump_17()
        {
            addFrameScript(0, this.frame1, 15, this.frame16, 31, this.frame32);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:BlackMageExt;
            var _local_7:*;
            var _local_8:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            this.xframe = "midair";
            this.done = false;
            if (((((parent) && (SSF2API.isReady())) && (this.self)) && (this.self.getGlobalVariable("screwAttackOn"))))
            {
                this.self.endAttack();
                this.self.forceAttack("item_screw");
            };
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

