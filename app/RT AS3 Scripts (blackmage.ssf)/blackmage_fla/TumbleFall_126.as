// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.TumbleFall_126

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class TumbleFall_126 extends MovieClip 
    {

        internal var hand:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var self:BlackMageExt;

        public function TumbleFall_126()
        {
            addFrameScript(0, this.frame1);
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


    }
}//package blackmage_fla

